from block import Block
from utils import pow
from Connect import Connect
from ConnectRemote import ConnectRemote
from ConnectData import ConnectData
from MerkleTree import MerkleTree

import logging
import sys
import threading
import time

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from block import HASH_PREV_BLOCK_KEY, HASH_MERKLE_ROOT_KEY, TIME_KEY


class Miner:
    mode = None  # PoW or BFT
    block_size = None
    blocks = None  # Current blocks in the chain
    difficulty = None
    curr_block = None
    credits = None
    mining_thread = None
    transactions_queue = None
    logger = None

    def __init__(self, id=None, mode='PoW', block_size=200, difficulty=3, port=0000, ip="000", local_ip="000"):
        self.id = id
        self.mode = mode
        self.block_size = block_size
        self.blocks = []
        self.difficulty = difficulty
        self.curr_block = Block(block_size=block_size)
        self.credits = {0: sys.float_info.max}
        if port != 0000:
            self.connect = Connect(port, {ConnectData.TYPE_TRANSACTION: self.add_transaction, ConnectData.TYPE_BLOCK: self.add_block, ConnectData.TYPE_MESSAGE: self.print_msg})
        if ip != "000":
            self.connect = ConnectRemote(ip,local_ip, {ConnectData.TYPE_TRANSACTION: self.add_transaction, ConnectData.TYPE_BLOCK: self.add_block, ConnectData.TYPE_MESSAGE: self.print_msg})
        self.transactions_queue = []
        self.blocks_queue = []
        self.lock = threading.Lock()
        self.__setup_logger()
        self.main_thread = threading.Thread(target=self.__run).start()

    def __setup_logger(self):
        self.logger = logging.getLogger("miner-{}-logger".format(self.id))
        handler = logging.FileHandler("miner-{}-logs.txt".format(self.id))
        handler.setFormatter(logging.Formatter(' %(name)s :: %(levelname)-8s :: %(message)s'))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def __run(self):
        while True:
            if len(self.blocks_queue) != 0:
                self.__validate_received_blocks()
            elif len(self.curr_block.data) == self.block_size:
                self.__mine_block()
            else:
                self.__move_transaction_to_block()

    def __move_transaction_to_block(self):
        self.lock.acquire()
        released = False
        if len(self.transactions_queue) != 0:
            transaction = self.transactions_queue[0]
            self.transactions_queue = self.transactions_queue[1:]
            self.lock.release()
            released = True
            if self.__verify_transaction(transaction):
                self.__update_credits(transaction)
                self.curr_block.add_transaction(transaction)
        if not released:
            self.lock.release()

    def add_block(self, block):  # This is going to be used with PoW and will assume a block is trusted
        self.logger.info("Received a block! with header: {} and hash: {}".format(block.header, block.hash_value))
        self.lock.acquire()
        self.blocks_queue.append(block)
        self.lock.release()
     
    def add_transaction(self, transaction):
        self.lock.acquire()
        self.transactions_queue.append(transaction)
        self.lock.release()

    def __update_curr_block(self, block):
        refined_data = []
        for curr_transaction in self.curr_block.data:
            found = False
            for transaction in block.data:
                if transaction.id == curr_transaction.id:
                    found = True
                    break
            if not found:
                refined_data.append(curr_transaction)
        self.curr_block.set_data(refined_data)

    def __mine_block(self):
        curr_time = time.time_ns()
        if self.mode == 'PoW':
            self.curr_block.set_header({
                HASH_PREV_BLOCK_KEY: self.blocks[-1].hash_value if len(self.blocks) > 0 else "",
                HASH_MERKLE_ROOT_KEY: MerkleTree(Transactions=self.curr_block.data).GetRoot(),
                TIME_KEY: str(curr_time)
            })
            header, hashed_header = pow(self.curr_block.header, self.difficulty)
            self.curr_block.set_header(header)
            self.curr_block.set_hash(hashed_header)
            self.curr_block.set_mining_time(time.time_ns() - curr_time)
            self.__add_block_to_chain()
        else:
            raise Exception("Not implemented Yet!")

    def __reverse_curr_block(self):
        for trans in self.curr_block.data:
            self.__update_credits(trans, True)
        self.transactions_queue = self.curr_block.data + self.transactions_queue
        self.curr_block = Block(block_size=self.block_size)

    def __can_add_external_block(self, external_block):
        if len(self.blocks) == 0:
            return True
        if self.blocks[-1].hash_value == external_block.header[HASH_PREV_BLOCK_KEY]:
            return True
        return False

    def __validate_received_blocks(self):
        new_blocks = False
        self.lock.acquire()
        while len(self.blocks_queue) != 0:
            if self.__can_add_external_block(self.blocks_queue[0]):
                self.__reverse_curr_block()
                new_blocks = True
                self.blocks.append(self.blocks_queue[0])
                self.logger.info(
                    "Received block added as {}: {}".format(len(self.blocks), self.blocks_queue[0])
                )
            else:
                self.logger.info(
                    "Received block rejected: {}".format(self.blocks_queue[0])
                )
            self.blocks_queue = self.blocks_queue[1:]
        self.lock.release()
        return new_blocks

    def __add_block_to_chain(self):
        new_blocks = self.__validate_received_blocks()
        if new_blocks:
            return
        self.blocks.append(self.curr_block)
        self.logger.info(
            "Mined block added as {}: {}".format(len(self.blocks), self.curr_block)
        )
        self.connect.send_to_all_miners(ConnectData.TYPE_BLOCK, self.curr_block)
        self.curr_block = Block(block_size=self.block_size)

    def __get_credit(self, node):
        return self.credits[node] if node in self.credits else 0

    def __update_credits(self, transaction, reverse=False):
        source = transaction.inputs[0][0]
        for output in transaction.outputs:
            target, value = output[0], output[1]
            if target not in self.credits:
                self.credits[target] = 0
            self.credits[target] += value if not reverse else -value
            self.credits[source] -= value if not reverse else -value

    def __verify_transaction(self, transaction):
        if not verify_signature(transaction):
            print("INVALID SIGNATURE {}".format(transaction.id))
            return False
        source = transaction.inputs[0][0]
        total_owned = self.__get_credit(source)
        total_spent = 0
        for output in transaction.outputs:
            total_spent += output[1]
        total_owned += 1e-5
        if total_owned < total_spent:
            self.logger.info("Verifying transaction {} failed, total_owned = {}, total_spent = {}".format(
                transaction.id, total_owned, total_spent
            ))
            # print(transaction)
        return total_owned >= total_spent

    def print_msg(self, msg):
        print(msg)


def verify_signature(transaction):
    return True
    try:
        transaction.inputs[0][1].verify(
            signature=transaction.signature,
            data=transaction.__str__().encode('utf-8'),
            padding=padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            algorithm=hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False


def main(argv):
    Miner(id=int(argv[0]), block_size=int(argv[1]), difficulty=int(argv[2]), port=int(argv[3]))


if __name__ == "__main__":
    main(sys.argv[1:])
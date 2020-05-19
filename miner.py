from block import Block
from utils import pow
from Connect import Connect
from ConnectData import ConnectData
from MerkleTree import MerkleTree


import sys
import threading
from datetime import datetime

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


    def __init__(self, mode='PoW', block_size=200, difficulty=3, port=0000):
        self.mode = mode
        self.block_size = block_size
        self.blocks = []
        self.difficulty = difficulty
        self.curr_block = Block(block_size=block_size)
        self.credits = {0: sys.float_info.max}
        self.connect = Connect(port, {ConnectData.TYPE_TRANSACTION: self.add_transaction})
        self.transactions_queue = []
        self.blocks_queue = []
        self.lock = threading.Lock()
        self.main_thread = threading.Thread(target=self.__run).start()
        self.ready_block = None

    def __run(self):
        while True:
            if len(self.curr_block.data) == self.block_size:
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
        curr_time = datetime.now()
        if self.mode == 'PoW':
            self.curr_block.set_header({
                HASH_PREV_BLOCK_KEY: self.blocks[-1].hash_value if len(self.blocks) > 0 else "",
                HASH_MERKLE_ROOT_KEY: MerkleTree(Transactions=self.curr_block.data).GetRoot(),
                TIME_KEY: str(datetime.now())
            })
            header, hashed_header = pow(self.curr_block.header, self.difficulty)
            self.curr_block.set_header(header)
            self.curr_block.set_hash(hashed_header)
            self.curr_block.set_mining_time(datetime.now() - curr_time)
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
        if self.blocks[-1].hash_value == external_block.headers[HASH_PREV_BLOCK_KEY]:
            return True
        return False

    def __add_block_to_chain(self):
        new_blocks = False
        self.lock.acquire()
        while len(self.blocks_queue) != 0:
            if self.__can_add_external_block(self.blocks_queue[0]):
                self.__reverse_curr_block()
                self.blocks_queue = self.blocks_queue[1:]
                new_blocks = True
        self.lock.release()
        if new_blocks:
            return
        self.blocks.append(self.curr_block)
        print(
            "Block {} has a has a hash value {} with mining time (h:mm:ss) = {} and headers {}".format(
                len(self.blocks), self.curr_block.hash_value, self.curr_block.mining_time, self.curr_block.header
            )
        )
        self.curr_block = Block(block_size=self.block_size)
        # TODO: let the network know!

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
            print("verifying transaction {} failed, total_owned = {}, total_spent = {}".format(transaction.id, total_owned, total_spent))
            # print(transaction)
        return total_owned >= total_spent


def verify_signature(transaction):
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

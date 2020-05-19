from block import Block
from utils import pow
from Connect import Connect
from ConnectData import ConnectData
from MerkleTree import MerkleTree


import sys
import multiprocessing
from datetime import datetime

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from block import HASH_PREV_BLOCK_KEY, HASH_MERKLE_ROOT_KEY, TIME_KEY, NONCE_KEY


class Miner:
    mode = None  # PoW or BFT
    block_size = None
    blocks = None  # Current blocks in the chain
    difficulty = None
    curr_block = None
    credits = None
    mining_process = None


    def __init__(self, mode='PoW', block_size=200, difficulty=3, port=0000):
        self.mode = mode
        self.block_size = block_size
        self.blocks = []
        self.difficulty = difficulty
        self.curr_block = Block(block_size=block_size)
        self.credits = {0: sys.float_info.max}
        self.connect = Connect(port, {ConnectData.TYPE_TRANSACTION: self.add_transaction})

    def add_block(self, block):  # This is going to be used with PoW and will assume a block is trusted
        self.blocks.append(block)  # Add to the chain
        self.__update_curr_block(block)  # Update current block to remove already added transactions
     
    def add_transaction(self, transaction):
        print("Adding Transaction")
        if self.__verify_transaction(transaction):
            self.__update_credits(transaction)
            self.curr_block.add_transaction(transaction)
            if len(self.curr_block.data) == self.block_size:
                self.__mine_block()
            return True
        else:
            return False

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
            self.blocks.append(self.curr_block)
            self.curr_block = Block(block_size=self.block_size)
        else:
            raise Exception("Not implemented Yet!")
        # self.mining_process = multiprocessing.Process(target=pow, args=(self.curr_block.header, self.difficulty))

    def __get_credit(self, node):
        return self.credits[node] if node in self.credits else 0

    def __update_credits(self, transaction):
        source = transaction.inputs[0][0]
        for output in transaction.outputs:
            target, value = output[0], output[1]
            if target not in self.credits:
                self.credits[target] = 0
            self.credits[target] += value
            self.credits[source] -= value

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
            print(transaction)
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

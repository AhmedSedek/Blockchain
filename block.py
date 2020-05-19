from hashlib import sha256

HASH_PREV_BLOCK_KEY = 'hashPrevBlock'
HASH_MERKLE_ROOT_KEY = 'hashMerkleRoot'
TIME_KEY = 'time'
NONCE_KEY = 'nonce'


class Block:
    header = None  # A dictionary with keys: HASH_PREV_BLOCK_KEY, HASH_MERKLE_ROOT_KEY, TIME_KEY, NONCE_KEY
    data = None  # List of transactions
    block_size = None

    hash_value = None  # 256-bit (64 Hex Ascii chars)

    mining_time = None

    def __init__(self, block_size=200):
        self.header = {}
        self.data = []
        self.block_size = block_size
        self.mining_time = 0

    def add_transaction(self, transaction):
        if len(self.data) == self.block_size:
            raise Exception("Block is already full!")
        self.data.append(transaction)

    def set_header(self, header):
        self.header = header

    def set_data(self, data):
        if len(data) > self.block_size:
            raise Exception("Number of transactions must be <= block_size")
        self.data = data

    def set_hash(self, hash_value):
        self.hash_value = hash_value

    def set_mining_time(self, time):
        self.mining_time = time

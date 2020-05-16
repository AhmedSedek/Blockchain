from hashlib import sha256

HASH_PREV_BLOCK_KEY = 'hashPrevBlock'
HASH_MERKLE_ROOT_KEY = 'hashMerkleRoot'
TIME_KEY = 'time'
NONCE_KEY = 'nonce'


class Block:
    header = None  # A dictionary with keys: HASH_PREV_BLOCK_KEY, HASH_MERKLE_ROOT_KEY, TIME_KEY, NONCE_KEY
    data = None  # List of transactions
    block_size = None

    __hash_value = None  # 256-bit (64 Hex Ascii chars)

    def __init__(self, header={}, data=[], block_size=200):
        self.header = header
        self.data = data
        self.block_size = block_size

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

    def get_hash(self):
        if self.__hash_value is None:
            self.__hash_value = self.__calculate_hash()
        return self.__hash_value

    def __calculate_hash(self):
        header_hex = (self.header[HASH_PREV_BLOCK_KEY] + self.header[HASH_MERKLE_ROOT_KEY]
                      + '{0:08X}'.format(self.header[TIME_KEY]) + '{0:08X}'.format(self.header[NONCE_KEY]))
        header_bin = header_hex.decode('hex')
        hash = sha256(sha256(header_bin).digest()).digest()
        hash[::-1].encode('hex_codec')
        return hash

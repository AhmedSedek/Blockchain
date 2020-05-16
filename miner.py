from block import Block


class Miner:
    mode = None  # PoW or BFT
    block_size = None
    blocks = None  # Current blocks in the chain
    difficulty = None
    curr_block = None

    def __init__(self, blocks=[], mode='PoW', block_size=200, difficulty=3):
        if len(blocks) == 0:
            raise Exception("There should be at least an initial block")
        self.mode = mode
        self.block_size = block_size
        self.blocks = blocks
        self.difficulty = difficulty
        self.curr_block = Block()

    def set_blocks(self, blocks):
        self.blocks = blocks

    def add_block(self, block):  # This is going to be used with PoW and will assume a block is trusted
        self.blocks.append(block)  # Add to the chain
        self.__update_curr_block(block)  # Update current block to remove already added transactions

    def vote_for_block(self, block):  # This is going to be used with BFT somehow
        raise Exception('not implemented yet @vote_for_block!')

    def add_transaction(self, transaction):
        if self.__verify_transaction(transaction):
            self.curr_block.data.append(transaction)
            if len(self.curr_block.data) == self.block_size:
                self.__mine_block()
        else:
            print("rejected transaction {}".format(transaction.id))

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
        raise Exception("Not implemented yet @__mind_block!")

    def __verify_transaction(self):
        # TODO Add actual imp.
        return True

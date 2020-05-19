from client import produce_transactions
from miner import Miner

def main():
    print("Welcome to the simple Blockchain project!")
    transactions, clients = produce_transactions("txdataset_v2.txt", 1000)
    miner = Miner(block_size=100, difficulty=20)
    for transaction in transactions:
        miner.add_transaction(transaction)
    for idx, block in enumerate(miner.blocks):
        print(
            "Block {} has a has a hash value {} with mining time (h:mm:ss) = {} and headers {}".format(
                idx, block.hash_value, block.mining_time, block.header
            )
        )

main()

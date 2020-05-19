from client import produce_transactions
from miner import Miner


def main():
    print("Welcome to the simple Blockchain project!")
    transactions, clients = produce_transactions("txdataset_v2.txt")
    miner = Miner(block_size=1000, difficulty=20)
    for transaction in transactions:
        miner.add_transaction(transaction)
    for idx, block in enumerate(miner.blocks):
        print(
            "Block {} has a has a hash value {} with mining time (h:mm:ss) = {}".format(
                idx, block.hash_value, block.mining_time
            )
        )


main()

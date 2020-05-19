from client import produce_transactions
from miner import Miner
from Connect import Connect
from ConnectData import ConnectData

def main():
    print("Welcome to the simple Blockchain project!")
    transactions, clients = produce_transactions("txdataset_v2.txt", 1000)
    miner = Miner(block_size=100, difficulty=20, port=65434)

    main_connect = Connect(65430)

    for transaction in transactions:
        main_connect.send_to_all_miners(ConnectData.TYPE_TRANSACTION, transaction)

main()

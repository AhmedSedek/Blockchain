from client import produce_transactions
from miner import Miner
from Connect import Connect
from ConnectData import ConnectData

def main():
    print("Welcome to the simple Blockchain project!")
    transactions, clients = produce_transactions("txdataset_v2.txt", 40)

    main_connect = Connect(65430)
    # miner0 = Miner(id=0, block_size=100, difficulty=20, port=65434, main_connect=main_connect)
    # miner1 = Miner(id=1, block_size=100, difficulty=20, port=65435, main_connect=main_connect)
    # miner2 = Miner(id=2, block_size=100, difficulty=20, port=65436, main_connect=main_connect)

    # miner1 = Miner(id=0, block_size=100, difficulty=20, port=65434)

    for transaction in transactions:
        main_connect.send_to_all_miners(ConnectData.TYPE_TRANSACTION, transaction)

main()

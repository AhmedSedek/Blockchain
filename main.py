from client import produce_transactions
from miner import Miner
from Connect import Connect
from ConnectData import ConnectData
from ConnectRemote import ConnectRemote


def main():
    print("Welcome to the simple Blockchain project!")
    transactions, clients = produce_transactions("txdataset_v2.txt", 40)

    remote_network = False
    main_connect = Connect(65430)  #To send over Local Network
    if remote_network:
        main_connect = ConnectRemote("192.168.1.7", False) # To send over Remote Network

    # miner0 = Miner(id=0, block_size=100, difficulty=20, port=65434, main_connect=main_connect)
    # miner1 = Miner(id=1, block_size=100, difficulty=20, port=65435, main_connect=main_connect)
    # miner2 = Miner(id=2, block_size=100, difficulty=20, port=65436, main_connect=main_connect)

    # miner1 = Miner(id=0, block_size=100, difficulty=20, port=65434)

    for transaction in transactions:
        main_connect.send_to_all_miners(ConnectData.TYPE_TRANSACTION, transaction)

main()

from Connect import Connect
from ConnectData import ConnectData


def miner1(data):
    print("I'm miner 1 received ", data)

def miner2(data):
    print("I'm miner 2 received ", data)

def miner3(data):
    print("I'm miner 3 received ", data)

miner1 = Connect(65433, {ConnectData.TYPE_TRANSACTION: miner1})
miner2 = Connect(65434, {ConnectData.TYPE_TRANSACTION: miner2})
miner3 = Connect(65435, {ConnectData.TYPE_TRANSACTION: miner3})

while True:
    m = input("Transaction Msg " )
    miner1.send_to_all_miners(ConnectData.TYPE_TRANSACTION, m)

    m = input("Transaction Msg ")
    miner2.send_to_all_miners(ConnectData.TYPE_TRANSACTION, m)



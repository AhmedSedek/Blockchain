from Connect import Connect
from ConnectData import ConnectData


def miner1(data):
    print("I'm miner 1 received ", data)

def miner2(data):
    print("I'm miner 2 received ", data)

def miner3(data):
    print("I'm miner 3 received ", data)

def miner2_second_callback(data):
    print("I'm miner 2 received Second callback", data)

miner1 = Connect(65433, {ConnectData.TYPE_TRANSACTION: miner1})
miner2 = Connect(65434, {ConnectData.TYPE_TRANSACTION: miner2, ConnectData.TYPE_BLOCK: miner2_second_callback})
miner3 = Connect(65435)

# client1 = Connect(65430, {ConnectData.TYPE_TRANSACTION: miner3})
# client2= Connect(65431, {ConnectData.TYPE_TRANSACTION: miner3})
# client3 = Connect(65432, {ConnectData.TYPE_TRANSACTION: miner3})
# client4 = Connect(65433, {ConnectData.TYPE_TRANSACTION: miner3})

while True:
    # m = input("Test Msg " )
    # miner1.send_to_all_miners(ConnectData.TYPE_TRANSACTION, m)

    m = input("Test Msg ")
    miner3.send_to_all_miners(ConnectData.TYPE_BLOCK, m)



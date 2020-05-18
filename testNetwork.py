from Connect import Connect
from Dummy import Dummy

miner1 = Connect(65433)
miner2 = Connect(65434)


while True:
    m = input("Transaction Msg " )
    miner1.broadcast_transaction(Dummy(m))



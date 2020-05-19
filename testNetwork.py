# from Connect import Connect
from ConnectData import ConnectData
from ConnectRemote import ConnectRemote
from miner import Miner


# client = ConnectRemote("127.0.0.1")
# client.send_to_all_miners(ConnectData.TYPE_MESSAGE, "Hello")

Miner(id=0, block_size=100, difficulty=20, ip="41.35.231.121")

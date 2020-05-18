import socket, pickle
import _thread
from ConnectData import ConnectData
from threading import Lock

s_print_lock = Lock()
HOST = "127.0.0.1"
MINERS_PORT_LIST = [65433, 65434]
CLIENTS_PORT_LIST = []

def t_print(*a, **b):
    with s_print_lock:
        print(*a, **b)

class Connect:

    def __init__(self, port):
        self.PORT = port

        _thread.start_new_thread(self._receiver, ())


    def broadcast_transaction(self, transaction):
        print(transaction)
        for port in MINERS_PORT_LIST:
            if port != self.PORT:
                print("sending to", port)
                connect_data = ConnectData(ConnectData.TYPE_TRANSACTION, transaction)
                data = pickle.dumps(connect_data)
                self._send(port, data)


    def _send(self, port, data):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, port))
            s.sendall(data)

    def _receiver(self):
        t_print("Connect ", self.PORT, " Received data")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, self.PORT))
            s.listen()
            while True:
                conn, addr = s.accept()
                data = []
                with conn:
                    print('Im ', HOST, ' Connected by', addr)
                    while True:
                        chunk = conn.recv(4096)
                        if not chunk:
                            break
                        data.extend(chunk)

                    transaction = pickle.loads(bytes(data)).get_data()
                    transaction.get_msg()


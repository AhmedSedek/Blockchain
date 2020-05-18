import socket, pickle
import _thread
from ConnectData import ConnectData
from threading import Lock

s_print_lock = Lock()
HOST = "127.0.0.1"
MINERS_PORT_LIST = [65433, 65434, 65435]
CLIENTS_PORT_LIST = []

def t_print(*a, **b):
    with s_print_lock:
        print(*a, **b)

class Connect:

    def __init__(self, port, callbacks):
        self.PORT = port
        self.callbacks = callbacks

        _thread.start_new_thread(self._receiver, ())

    def send_to_all_miners(self, data_type, data):
        connect_data = ConnectData(data_type, data)
        data = pickle.dumps(connect_data)
        for port in MINERS_PORT_LIST:
            if port != self.PORT:
                t_print("sending to", port)
                self._send(port, data)

    def send_to_miner(self, port, data_type, data):
        connect_data = ConnectData(data_type, data)
        data = pickle.dumps(connect_data)
        t_print("sending to", port)
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

                    connect_data = pickle.loads(bytes(data))
                    data_type = connect_data.TYPE
                    data = connect_data.get_data()
                    self.callbacks[data_type](data)


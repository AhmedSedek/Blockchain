import socket, pickle
import _thread
from ConnectData import ConnectData
from threading import Lock

s_print_lock = Lock()
HOST = "127.0.0.1"
CLIENTS_PORT_LIST = [65430, 65431, 65432, 65433]
# Sami / Mazen / Sharaf
MINERS_IP_LIST = ["197.55.197.67", "197.35.101.30", "41.35.231.121"]

def t_print(*a, **b):
    with s_print_lock:
        print(*a, **b)

class ConnectRemote:

    def __init__(self, ip, local_ip, callbacks = {}, can_receive=True):
        print("Initialize Remote Connection")
        self.IP = ip
        self.LOCAL_IP = local_ip
        self.callbacks = callbacks

        if can_receive: _thread.start_new_thread(self._receiver, ())

    def send_to_all_miners(self, data_type, data):
        self._send_to_all_ports(MINERS_IP_LIST, "Miner", data_type, data)

    # def send_to_all_clients(self, data_type, data):
    #     self._send_to_all_ports(CLIENTS_PORT_LIST, "Client", data_type, data)

    def send_to_miner(self, port, data_type, data):
        self._send_to_ip("Miner", port, data_type, data)

    # def send_to_client(self, port, data_type, data):
    #     self._send_to_port("Client", port, data_type, data)

    def _send_to_ip(self, kind, ip, data_type, data):
        connect_data = ConnectData(data_type, data)
        data = pickle.dumps(connect_data)
        t_print("sending to", kind, ip)
        try:
            self._send(ip, data)
        except (ValueError, Exception):
            t_print(kind, ip, "Not Connected")

    def _send_to_all_ports(self, port_list, kind,  data_type, data):
        connect_data = ConnectData(data_type, data)
        data = pickle.dumps(connect_data)
        for ip in port_list:
            if ip != self.IP:
                t_print("sending to", ip)
                try:
                    self._send(ip, data)
                except (ValueError, Exception):
                    t_print(kind,ip, "Not Connected")

    def _send(self, ip, data):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, 65432))
            s.sendall(data)

    def _receiver(self):
        t_print("Connection", self.IP, "Ready to Receive Data")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.LOCAL_IP, 65432))
            s.listen(4)
            while True:
                conn, addr = s.accept()
                data = []
                with conn:
                    # print('Im ', HOST, ' Connected by', addr)
                    while True:
                        chunk = conn.recv(4096)
                        if not chunk:
                            break
                        data.extend(chunk)

                    connect_data = pickle.loads(bytes(data))
                    data_type = connect_data.TYPE
                    data = connect_data.get_data()
                    t_print("Received new", data_type)
                    try:
                        self.callbacks[data_type](data)
                    except (ValueError, Exception):
                        t_print("No Supported Callback")



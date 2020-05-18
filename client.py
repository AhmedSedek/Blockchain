from transaction import Transaction
import cryptography
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa


class Client:

    def __init__(self, id):
        self.id = id
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()


def produce_transactions(path):
    clients = {}
    transactions = []
    with open(path) as fp:
        lines = fp.read().split("\n")[:-1]
        for line in lines[1:]:
            fields = line.split('\t')
            trans_id = int(fields[0])
            trans = Transaction(trans_id)
            prev_tans = None
            outputs = {}
            for field in fields[1:]:
                if field.startswith("intput"):
                    input_ip = field.split(':')[1]
                    add_client(clients, input_ip)
                elif field.startswith("outputindex"):
                    output_index = int(field.split(':')[1])
                elif field.startswith("output"):
                    output_num = field.split(':')[0][6:]
                    if output_num == "":
                        output_num = 1
                    else:
                        output_num = int(output_num)
                    output_ip = int(field.split(':')[1])
                    add_client(clients, output_ip)
                    if output_num in outputs:
                        outputs[output_num] = (output_ip, outputs[output_num][1])
                    else:
                        outputs[output_num] = (output_ip, None)
                elif field.startswith("value"):
                    output_num = field.split(':')[0][5:]
                    if output_num == "":
                        output_num = 1
                    else:
                        output_num = int(output_num)
                    value = float(field.split(':')[1])
                    if output_num in outputs:
                        outputs[output_num] = (outputs[output_num][0], value)
                    else:
                        outputs[output_num] = (None, value)
                elif field.startswith("previoustx"):
                    prev_tans = int(field.split(':')[1])
            for op in outputs.values():
                trans.add_output(op)
            trans.add_input((input_ip, prev_tans))
            transactions.append(trans)
            print(trans)



def add_client(clients, input_ip):
    if input_ip not in clients:
        clients[input_ip] = Client(input_ip)

from transaction import Transaction
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


class Client:
    def __init__(self, id):
        self.id = id
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()


def produce_transactions(path, cnt=None):
    clients = {}
    transactions = []
    with open(path) as fp:
        lines = fp.read().split("\n")[:-1]
        id = 0
        for line in lines[1:]:
            # print("Reading line:", line)
            id += 1
            if cnt is not None and id > cnt:
                break
            fields = line.split('\t')
            trans_id = int(fields[0])
            trans = Transaction(trans_id)
            outputs = {}
            for field in fields[1:]:
                if field.startswith("intput"):
                    input_ip = int(field.split(':')[1])
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
            for op in outputs.values():
                trans.add_output(op)
            # trans.add_input((input_ip, clients[input_ip].public_key))
            trans.add_input((input_ip, None))
            transactions.append(trans)
            signature = clients[input_ip].private_key.sign(
                data=trans.__str__().encode('utf-8'),
                padding=padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                algorithm=hashes.SHA256()
            )
            # trans.add_signature(signature)
    return transactions, clients


def add_client(clients, input_ip):
    if input_ip not in clients:
        clients[input_ip] = Client(input_ip)

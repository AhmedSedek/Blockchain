class Transaction:

    def __init__(self, id):
        if not isinstance(id, int):
            raise Exception("transaction id must be an int!")
        self.id = id
        self.outputs = []  # list of tuples (node_id, value)
        self.op_counter = 0
        self.ip_counter = 0
        self.signature = None
        self.inputs = []  # list of tuples (node_id, public_key)

    def add_input(self, ip):
        self.ip_counter = self.ip_counter + 1
        self.inputs.append(ip)

    def add_output(self, op):
        self.op_counter = self.op_counter + 1
        self.outputs.append(op)

    def add_signature(self, signature):
        self.signature = signature

    def __str__(self):
        res = str(self.id) + ':' + str(self.ip_counter) + ':'
        for ip in self.inputs:
            res += "({})".format(str(ip[0])) + ':'
        res += str(self.op_counter) + ':'
        for output in self.outputs:
            res += str(output) + ':'
        return res

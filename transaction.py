class Transaction:
    ip_counter = None
    inputs = []  # List of Pairs
    op_counter = None
    outputs = []  # List of Pairs

    def __init__(self, ip_counter=0, inputs=[], op_counter=0, outputs=[]):
        self.ip_counter = ip_counter
        self.inputs = inputs
        self.op_counter = op_counter
        self.outputs = outputs
        if ip_counter != len(inputs):
            raise Exception("ip_counter and inputs length don't match!")
        if op_counter != len(outputs):
            raise Exception("op_counter and outputs length don't match!")

    def add_input(self, ip):
        self.ip_counter = self.input_counter + 1
        self.inputs.append(ip)

    def add_output(self, op):
        self.op_counter = self.op_counter + 1
        self.outputs.append(op)

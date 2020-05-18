
class ConnectData:

    TYPE_TRANSACTION = "TRANSACTION"
    TYPE_PUBLIC_KEY = "PUBLIC_KEY"
    TYPE_BLOCK = "BLOCK"

    def __init__(self, data_type, data):
        self.TYPE = data_type
        self.data = data


    def get_data(self):
        return self.data
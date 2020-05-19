import hashlib
from collections import OrderedDict


class MerkleTree:
    Tree = []
    Root = None

    def __init__(self, Transactions=None):
        self.Transactions = Transactions
        self.transactionDictionary = OrderedDict()
        self.create_tree()

    def GetRoot(self):
        return self.Root

    def create_tree(self):
        Transactions = self.Transactions
        transactionDictionary = self.transactionDictionary
        temp_list = []
        size = len(Transactions)

        if size != 1:
            for i in range(0, size, 2):
                first_transaction = Transactions[i]

                if i + 1 != len(Transactions):
                    second_transaction = Transactions[i + 1]
                else:
                    second_transaction = ''

                first_transaction_hash = hashlib.sha256(first_transaction.__str__().encode('utf-8')).hexdigest()

                if second_transaction != '':
                    second_transaction_hash = hashlib.sha256(second_transaction.__str__().encode('utf-8')).hexdigest()

                transactionDictionary[Transactions[i]] = first_transaction_hash

                if second_transaction != '':
                    transactionDictionary[Transactions[i + 1]] = second_transaction_hash

                if second_transaction != '':
                    basehexin = int(first_transaction_hash, 16)
                    sechexin = int(second_transaction_hash, 16)
                    newHash = basehexin + sechexin
                    hexHash = hex(newHash)
                    temp_list.append(str(hexHash))
                else:
                    temp_list.append(first_transaction_hash)

            self.Tree.append(temp_list)
            if len(Transactions) != 1:
                self.Transactions = temp_list
                self.transactionDictionary = transactionDictionary
                self.create_tree()

        else :
            self.Root = Transactions[0]
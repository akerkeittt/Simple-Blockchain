import time
import hashlib


def simple_hash(text):
    hash_object = hashlib.sha256(text.encode())
    return hash_object.hexdigest()

class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
    
    def __str__(self):
        return f"{self.sender}->{self.receiver}:{self.amount}"

class MerkleTree:
    @staticmethod
    def create_merkle_root(transactions):
        hashes = []  
        for tx in transactions:  
            string_tx = str(tx)  
            tx_hash = simple_hash(string_tx)  
            hashes.append(tx_hash)  

        while len(hashes) > 1:
            temp_hashes = []
            for i in range(0, len(hashes), 2):
                left = hashes[i]
                right = hashes[i+1] if i+1 < len(hashes) else left  
                combined_hash = simple_hash(left + right)
                temp_hashes.append(combined_hash)
            hashes = temp_hashes
        
        return hashes[0] if hashes else None

class Block:
    def __init__(self, previous_hash, transactions, difficulty=2):
        self.previous_hash = previous_hash
        self.timestamp = time.time()
        self.transactions = transactions
        self.merkle_root = MerkleTree.create_merkle_root(transactions)
        self.nonce = 0
        self.difficulty = difficulty
        self.hash = self.mine_block()
    
    def mine_block(self):
        prefix = '0' * self.difficulty
        while True:
            block_data = f"{self.previous_hash}{self.timestamp}{self.merkle_root}{self.nonce}"
            block_hash = simple_hash(block_data)
            if block_hash.startswith(prefix):
                print(f"Block mined: {block_hash}")
                return block_hash
            self.nonce += 1
    
    def __str__(self):
        return f"Hash: {self.hash}, Previous Hash: {self.previous_hash}, Merkle Root: {self.merkle_root}, Nonce: {self.nonce}"

class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block("0", [Transaction("Genesis", "Genesis", 0)])
        self.chain.append(genesis_block)

    def add_block(self, transactions):
        previous_hash = self.chain[-1].hash
        new_block = Block(previous_hash, transactions)
        self.chain.append(new_block)

    def validate_blockchain(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            if current.previous_hash != previous.hash:
                return False
        return True

    def display_chain(self):
        for i, block in enumerate(self.chain):
            print(f"Block {i}")
            print(f"  Timestamp     : {time.ctime(block.timestamp)}")
            print(f"  Hash          : {block.hash}")
            print(f"  Previous Hash : {block.previous_hash}")
            print(f"  Merkle Root   : {block.merkle_root}")
            print(f"  Nonce         : {block.nonce}")
            print(f"  Transactions  :")
            for tx in block.transactions:
                print(f"    - {tx}")
            print("-" * 40)


if __name__ == "__main__":
    blockchain = Blockchain()
    
    transactions1 = [
    Transaction("Aruzhan", "Akerke", 50),
    Transaction("Dinara", "Laura", 100),
    Transaction("Aigul", "Aym", 150),
    Transaction("Aizere", "Meruert", 200),
    Transaction("Madina", "Gauhar", 250),
    Transaction("Aisha", "Nazerke", 300),
    Transaction("Aliya", "Elmira", 350),
    Transaction("Aydana", "Sholpan", 400),
    Transaction("Zhanar", "Inzhu", 450),
    Transaction("Ayaru", "Tomiris", 500)
]
    transactions2 = [
    Transaction("Charlie", "David", 15), 
    Transaction("Eve", "Frank", 40),
    Transaction("Alice", "Eve", 10)
]
    
    print("\nAdding Block 1...")
    blockchain.add_block(transactions1)
    
    print("\nAdding Block 2...")
    blockchain.add_block(transactions2)

    
    print("\nBlockchain:")
    blockchain.display_chain()
    
    print("\nValidating Blockchain:")
    is_valid = blockchain.validate_blockchain()
    print("Blockchain is valid" if is_valid else "Blockchain is corrupted")

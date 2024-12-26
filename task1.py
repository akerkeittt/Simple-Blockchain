import time

K = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
]

def right_rotate(value, shift):
    return (value >> shift) | (value << (32 - shift)) & 0xFFFFFFFF

def sha256_padding(message):
    original_length = len(message) * 8
    message += b'\x80'
    while len(message) % 64 != 56:
        message += b'\x00'
    message += original_length.to_bytes(8, 'big')
    return message

def sha256(message):
    H = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
    ]

    message = sha256_padding(message)

    for i in range(0, len(message), 64):
        block = message[i:i + 64]
        W = [int.from_bytes(block[j:j + 4], 'big') for j in range(0, 64, 4)]
        for j in range(16, 64):
            s0 = right_rotate(W[j - 15], 7) ^ right_rotate(W[j - 15], 18) ^ (W[j - 15] >> 3)
            s1 = right_rotate(W[j - 2], 17) ^ right_rotate(W[j - 2], 19) ^ (W[j - 2] >> 10)
            W.append((W[j - 16] + s0 + W[j - 7] + s1) & 0xFFFFFFFF)

        a, b, c, d, e, f, g, h = H

        for j in range(64):
            S1 = right_rotate(e, 6) ^ right_rotate(e, 11) ^ right_rotate(e, 25)
            ch = (e & f) ^ (~e & g)
            temp1 = (h + S1 + ch + K[j] + W[j]) & 0xFFFFFFFF
            S0 = right_rotate(a, 2) ^ right_rotate(a, 13) ^ right_rotate(a, 22)
            maj = (a & b) ^ (a & c) ^ (b & c)
            temp2 = (S0 + maj) & 0xFFFFFFFF

            h = g
            g = f
            f = e
            e = (d + temp1) & 0xFFFFFFFF
            d = c
            c = b
            b = a
            a = (temp1 + temp2) & 0xFFFFFFFF

        H = [(x + y) & 0xFFFFFFFF for x, y in zip(H, [a, b, c, d, e, f, g, h])]

    return ''.join(f'{x:08x}' for x in H)


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
        if not transactions:
            return sha256(b"EMPTY")

        hashes = [sha256(str(tx).encode('utf-8')) for tx in transactions]  

        while len(hashes) > 1:
            temp_hashes = []
            for i in range(0, len(hashes), 2):
                left = hashes[i]
                right = hashes[i + 1] if i + 1 < len(hashes) else left
                combined_hash = sha256((left + right).encode('utf-8'))
                temp_hashes.append(combined_hash)
            hashes = temp_hashes
        
        return hashes[0]

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
            block_hash = sha256(block_data.encode('utf-8'))  
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
   
    blockchain.add_block(transactions1)
  
    blockchain.add_block(transactions2)

    
    print("\nBlockchain:")
    blockchain.display_chain()
    
    print("\nValidating Blockchain:")
    is_valid = blockchain.validate_blockchain()
    print("Blockchain is valid" if is_valid else "Blockchain is corrupted")

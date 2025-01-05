import math
import random

def is_prime(num):
    if num <= 1:
        return False
    for i in range(2, int(math.sqrt(num)) + 1):
        if num % i == 0:
            return False
    return True

def generate_prime():
    while True:
        num = random.randint(100, 999)
        if is_prime(num):
            return num

def generate_keys():
    p = generate_prime()
    q = generate_prime()
    while p == q:
        q = generate_prime()

    n = p * q
    phi = (p - 1) * (q - 1)

    e = random.randint(2, phi - 1)
    while math.gcd(e, phi) != 1:
        e = random.randint(2, phi - 1)

    d = pow(e, -1, phi)
    return (e, n), (d, n)

def encrypt(public_key, plaintext):
    e, n = public_key
    ciphertext = [pow(ord(char), e, n) for char in plaintext]
    return ciphertext

def decrypt(private_key, ciphertext):
    d, n = private_key
    plaintext = ''.join([chr(pow(char, d, n)) for char in ciphertext])
    return plaintext

def sign(private_key, document):
    d, n = private_key
    signature = [pow(ord(char), d, n) for char in document]
    return signature

def verify(public_key, document, signature):
    e, n = public_key
    decrypted_signature = ''.join([chr(pow(char, e, n)) for char in signature])
    return decrypted_signature == document

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
    def __init__(self, sender, receiver, amount, signature):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.signature = signature

    def __repr__(self):
        return f"Transaction(sender={self.sender}, receiver={self.receiver}, amount={self.amount}, signature={self.signature})"

class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []

    def add_transaction(self, transaction):
        if self.verify_transaction(transaction):
            self.pending_transactions.append(transaction)

    def verify_transaction(self, transaction):
        if not verify(transaction.sender, f"{transaction.receiver}{transaction.amount}", transaction.signature):
            raise ValueError("Signature is wrong")
        return True

    def mine_block(self):
        block_data = ''.join(map(str, self.pending_transactions))
        block_hash = sha256(block_data.encode())
        self.chain.append((self.pending_transactions, block_hash))
        self.pending_transactions = []

class Wallet:
    def __init__(self):
        self.private_key, self.public_key = generate_keys()

    def create_transaction(self, receiver, amount):
        document = f"{receiver}{amount}"
        signature = sign(self.private_key, document)
        return Transaction(self.public_key, receiver, amount, signature)

if __name__ == "__main__":
    blockchain = Blockchain()

    alice_wallet = Wallet()
    bob_wallet = Wallet()

    transaction = alice_wallet.create_transaction(bob_wallet.public_key, 50)
    blockchain.add_transaction(transaction)

    blockchain.mine_block()

    print("Blockchain:", blockchain.chain)

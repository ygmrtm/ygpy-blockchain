import json
import time as t
from hashlib import sha256


class Block:
    def __init__(self, index=0, version=0, previous_block=0, merkle_root=0, time=t.time()
                 , transactions=None, bits=0, nonce=0):
        if not transactions:
            transactions = []
        self.index = index
        self.version = version
        self.previous_block = previous_block
        self.merkle_root = merkle_root
        self.time = time
        self.transactions = transactions
        self.bits = bits
        self.nonce = nonce

    def __str__(self):
        return f'index:{self.index} | version:{self.version} | previous_block:{self.previous_block} \
        | merkle_root:{self.merkle_root} | time:{self.time} | transactions:{len(self.transactions)} | bits:{self.bits} \
        | nonce:{self.nonce} '

    @property
    def difficulty(self):
        i = 0
        for ch in self.bits[2:]:
            if ch == '0':
                i += 1
            else:
                break
        return i

    def compute_hash(self):
        """
        A function that return the hash of the block contents.
        """
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()

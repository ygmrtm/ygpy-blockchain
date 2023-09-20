import random

try:
    import pickle
    import time
    import sys
    import threading
    from entity.Block import Block
    # from entity.MerkleTree import MerkleTree
    from pymerkle import MerkleTree
    from entity.GeneticAlgorithm import Population
    from entity.GeneticAlgorithm import Phenotype

except ImportError as exc:
    print(exc)


class Blockchain:

    def __init__(self, azathoth=''):
        self.unconfirmed_transactions = []
        self.chain = []
        self.current_target = '0x0000ffffffffffffffffffffffffffff00000000000000000000000000000000'
        self.version = 1

        if not azathoth:
            self.create_genesis_block()

    def __str__(self):
        return print(str(self.chain[0]), f'unconfirmed_transactions={len(self.unconfirmed_transactions)}')

    @property
    def last_block(self):
        return self.chain[-1]

    @property
    def difficulty(self):
        i = 0
        for ch in self.current_target[2:]:
            if ch == '0':
                i += 1
            else:
                break
        return i

    def create_genesis_block(self):
        """
        A function to generate genesis block and appends it to
        the chain. The block has an index 0, previous_hash as 0, and
        a valid hash.
        """
        genesis_block = Block()
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    def adjust_target(self, first, last, expected_time_per_block=600):
        # 2. Work out the ratio of the actual time against the expected time
        actual = last - first  # number of seconds between first and last block
        ratio = actual / expected_time_per_block

        # 3. Limit the adjustment by a factor of 5 (to prevent massive changes from one target to the next)
        ratio = 0.15 / random.randrange(1, 4, 1) if ratio < 0.15 else random.randrange(4, 7, 1) if ratio > 4 else ratio
        print(f'{actual} secs w {ratio} ratio')
        print('adjusting target {}'.format('DOWN' if ratio < 1 else 'UP'))

        # 4. Multiply the current target by this ratio to get the new target
        current_target_int = int(self.current_target, 16)
        new_target_int = int(current_target_int * ratio)
        new_target = str(hex(new_target_int))
        print('' * 16, 'FROM:', current_target_int)
        print('' * 16, '  TO:', new_target_int)
        return new_target[0:2] + '0' * (66 - len(new_target)) + new_target[2:]

    def new_block(self):
        """
        This function serves as an interface to add the pending
        transactions to the blockchain by adding them to the block
        and figuring out Proof Of Work.
        """
        print('Difficulty={}\n{}'.format(self.difficulty, self.current_target))

        last_block = self.last_block
        tree = MerkleTree()
        # Populate tree with some records
        for record in self.unconfirmed_transactions:
            tree.encrypt(record)

        new_block = Block(index=last_block.index + 1, version=self.version, previous_block=last_block.hash
                          , merkle_root=tree.get_root_hash().decode("utf-8"), time=time.time()
                          , transactions=self.unconfirmed_transactions, bits=self.current_target, nonce=0)
        return new_block

    def mine(self, expected_time_per_block):
        block_proof = computed_hash = None
        new_block = self.new_block()
        if new_block:
            block_proof, computed_hash = self.proof_of_work(new_block, expected_time_per_block)
        return block_proof, computed_hash

    @staticmethod
    def proof_of_work_alternate(block, phenotype):
        print(f'>: proof_of_work_alternate {phenotype.up_down.upper()}'
              f' range[{phenotype.lower if phenotype.up_down == "down" else phenotype.value} to '
              f' {phenotype.value if phenotype.up_down == "down" else "INFINITE"}]')

        block.nonce = phenotype.value if phenotype.up_down == 'down' else phenotype.lower
        computed_hash = block.compute_hash()
        out_of_range = False
        while not ((computed_hash.startswith('0' * block.difficulty)
                    and int(block.bits, 16) - int(computed_hash, 16) > 0)
                   or out_of_range):
            if phenotype.up_down == 'down':
                block.nonce -= 1
                out_of_range = block.nonce < phenotype.lower
            else:
                block.nonce += 1
            computed_hash = block.compute_hash()

        return block, computed_hash

    def proof_of_work(self, block, expected_time_per_block):
        """
        Function that tries different values of nonce to get a hash
        that satisfies our difficulty criteria.
        """
        block.nonce = 0
        start = time.time()
        computed_hash = block.compute_hash()
        while not ((computed_hash.startswith('0' * self.difficulty)
                    and int(block.bits, 16) - int(computed_hash, 16) > 0)
                   or time.time() - start > (expected_time_per_block * 1.5)):
            block.nonce += 1
            computed_hash = block.compute_hash()
            if block.nonce % 1000000 == 0:
                print('nonce={} elapsed={} \n computed_hash={}... still far from get it'.format(block.nonce
                                                                                                , time.time() - start,
                                                                                                computed_hash))

        return block, computed_hash

    def add_block(self, block, proof):
        """
        A function that adds the block to the chain after verification.
        Verification includes:
        * Checking if the proof is valid.
        * The previous_hash referred in the block and the hash of the latest block
          in the chain match.
        """
        previous_hash = self.last_block.hash

        if previous_hash != block.previous_block or not self.is_valid_proof(block, proof):
            print("cannot add the block")
            return False

        block.hash = proof
        self.chain.append(block)
        return True

    def is_valid_proof(self, block, block_hash):
        """
        Check if block_hash is valid hash of block and satisfies
        the difficulty criteria.
        """
        return (block_hash.startswith('0' * self.difficulty)
                and int(block.bits, 16) - int(block_hash, 16) > 0
                and block_hash == block.compute_hash())

    def check_chain_validity(self):
        previous_hash = 0
        blocks_ok = 1
        for block in self.chain:
            block_prev_hash = block.previous_block
            delattr(block, "hash")
            block_hash = block.compute_hash()
            if previous_hash == block_prev_hash and int(str(block.bits), 16) - int(block_hash,
                                                                                   16) > 0 and block.index > 0:
                blocks_ok += 1
            block.hash, previous_hash = block_hash, block_hash
        return blocks_ok == len(self.chain)

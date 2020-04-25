#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
A simple blockchain implementation
Based on the original bitcoin and the example from
https://developer.ibm.com/technologies/blockchain/tutorials/develop-a-blockchain-application-from-scratch-in-python/
'''

from hashlib import sha256
import json
import time

class Block:
    "A single block that holds some data as a transaction"
    def __init__(self, index, transactions, timestamp, previous_hash):
        '''
        Create a block
        :param index: ID of the block
        :param transactions: data stored in the block
        :param timestamp: Time block was created
        :param previous_hash: hash of the previous block
        '''
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash

    def compute_hash(self):
        '''
        Compute the hash of this block
        '''
        b = json.dumps(self.__dict__, sort_keys=True)
        return sha256(b.encode()).hexdigest()


class Blockchain:
    "A chain of immutable blocks"
    def __init__(self, difficulty=2):
        '''
        Create the blockchain
        :param difficulty: Difficulty in perform the PoW
        '''
        b = Block(0, "", time.time(), "0")
        b.hash = b.compute_hash()
        self.chain = [b]
        self.difficulty = difficulty

    def proof_of_work(self, block):
        '''
        Prove that computational work was spent in creating the block
        :param block: The block to prove
        '''
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith("0" * self.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash

    def add_block(self, block, proof):
        '''
        Add a block to the chain if its proof is valid
        :param block: Block to add
        :param proof: Proof of work in adding the block
        '''
        previous_hash = self.last_block.hash
        if previous_hash != block.previous_hash:
            return False
        if not self.is_valid_proof(block, proof):
            return False
        block.hash = proof
        self.chain.append(block)
        return True

    def is_valid_proof(self, block, proof):
        '''
        Check whether a proof is valid
        :param block: Block to check
        :param proof: proof to check against the block
        '''
        return (proof.startswith("0" * self.difficulty)) and \
            (proof == block.compute_hash())

    def mine(self, transactions):
        '''
        Perfom computational work to add data to the chain
        '''
        b = Block(
            self.last_block.index + 1,
            transactions,
            time.time(),
            self.last_block.hash
        )
        p = self.proof_of_work(b)
        self.add_block(b, p)
        self.unconfirmed_trans = []
        return True

    @property
    def last_block(self):
        '''
        Get the last block in the chain
        '''
        return self.chain[-1]

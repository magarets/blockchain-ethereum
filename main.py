import hashlib
import datetime
import json
import random

class Node:
    def __init__(self):
        self.address = ''
        self.balance = 0
        self.chain = []
        self.trancetions = []

    def proof(self, block):
        difficulty = block['difficulty']

        hash = hashlib.sha256(json.dumps(block).encode()).hexdigest()
        if int(hash, 16) < int(difficulty, 16):
            return True

        return False

    def recvBlock(self, block):
        res = self.proof(block)

        if res:
            self.chain.append(block)

        self.trancetions = [] # 트랜잭션이 쌓이는거 방지

        return res

    def recvTransaction(self, transaction):
        sender = transaction['from']
        amount = transaction['amount']
        to = transaction['to']

        if sender == self.address:
            if amount > self.balance:
                return False
            self.balance -= amount

        if to == self.address:
            self.balance += amount

        self.trancetions.append(transaction)

        return True

    def sendTo(self, to, amount):
        transaction = {
            'from': self.address,
            'to': to,
            'amount': amount
        }

        return True

class Miner(Node):
    def __init__(self):
        super().__init__()

    def getMrklRoot(self, transactions):
        leafs = []
        for transactions in transactions:
            leaf = hashlib.sha256(json.dumps(transactions).encode()).hexdigest()
            leafs.append(leaf)

        if len(leafs) <= 0:
            return ''
        elif len(leafs) == 1:
            return leafs[0]

        while len(leafs) > 1:
            hashA = leafs.pop(0)
            hashB = leafs.pop(0)
            hashC = hashlib.sha256(''.join([hashA, hashB]).encode()).hexdigest()
            leafs.append(hashC)

        return leafs[0]

    def doMining(self):
        time = self.chain[len(self.chain) - 1]['time'] + 600
        block = {
            'ver': 1,
            'prev_hash': '',
            'mrkl_root': self.getMrklRoot(self.trancetions),
            'time': time,
            'difficulty': 'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff',  # 64
            'nonce': 0,
            'transactions': []
        }

        prevHash = ''
        if len(self.chain) > 0:
            prevBlock = self.chain[len(self.chain) - 1]
            prevHash = hashlib.sha256(json.dumps(prevBlock).encode()).hexdigest()

        block['transactions'] = self.trancetions
        block['prev_hash'] = prevHash

        difficulty = block['difficulty']

        while True:
            hash = hashlib.sha256(json.dumps(block).encode()).hexdigest()
            if int(hash, 16) < int(difficulty, 16):
                break

            block['nonce'] += 1

        return block

nodes = []
nodeCount = 5
limit = 20

def getGenBlock():
    block = {
        'ver' : 1,
        'prev_hash': '',
        'mrkl_root': '',
        'time': datetime.datetime.now().timestamp(),
        'difficulty': 'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff', # 64
        'nonce': 0,
        'transactions': []
    }

    difficulty = block['difficulty']

    while True:
        hash = hashlib.sha256(json.dumps(block).encode()).hexdigest()
        if int(hash, 16) < int(difficulty, 16):
            break

        block['nonce'] += 1

    return block

def init():
    genBlock = getGenBlock()

    miner = Miner()
    miner.address = hashlib.sha256(str(0).encode()).hexdigest()
    miner.recvBlock(genBlock)
    nodes.append(miner)

    for i in range(1, nodeCount):
        node = Node()
        node.address = hashlib.sha256(str(0).encode()).hexdigest()
        node.recvBlock(genBlock)
        nodes.append(node)

    return True

def broadcastBlock(block):
    for i in range(0, nodeCount):
        nodes[i].recvBlock(block)

    return True

def broadcastTransaction(transaction):
    for i in range(0, nodeCount):
        nodes[i].recvTransaction(transaction)

    return True

init()
repeat = 0
while repeat < limit:
    # 블록 만들기
    for i in range(0, nodeCount):
        # 트랜젝션 일으키기. 각 노드 번갈아 가면서
        if random.randint(0, 1) > 0:
            # 50 % 확률로 트랙잭션 발생
            sender = nodes[i]

            if sender.balance < 1:
                continue

            sel = i
            while sel == i:
                sel = random.randint(0, nodeCount - 1)

            to = nodes[sel]
            amount = random.randint(0, sender.balance) # 0부터 잔액한도내에서 랜덤

            transaction = sender.sendTo(to.address, amount)
            broadcastTransaction(transaction)

    miner = nodes[0]
    candBlock = miner.doMining()
    if broadcastBlock(candBlock):
        print('+ Mining block' + str(repeat + 1) + '---------')
        print('hash: ', hashlib.sha256(json.dumps(candBlock).encode()).hexdigest())
        print('nonce: ' + str(candBlock['nonce']))

    repeat += 1
import sys


class SmoothWRR:
    def __init__(self):
        self.names = []
        self.weights = []
        self.current = []

    def set_pool(self, entries):
        self.names, self.weights, self.current = [], [], []
        self.W = 0
        for e in entries:
            name, sep, w = e.rpartition('=')
            if not sep:
                name, w = e, '1'
            self.names.append(name)
            self.weights.append(int(w))
            self.W += int(w)
            self.current.append(0)

    def pick(self):
        # TODO: smooth weighted round-robin.
        #   1. add every weight to its backend's current score
        #   2. the highest score wins; the earliest listed wins a tie
        #   3. subtract the total of all weights from the winner
        # Answer 'EMPTY' when no backend has a weight above 0.
        allZero = True
        maxCurr, maxInd = self.current[0], 0
        for i in range(len(self.current)):
            if(self.current[i]!=0): 
                allZero = False
            if(maxCurr<self.current[i]):
                maxCurr = self.current[i]
                maxInd = i

        if allZero: return 'EMPTY'

        for i in range(len(self.current)):
            self.current[i] += self.weights[i] if i!=maxInd or allZero else -(self.W)

        return self.names[maxInd] 


def main():
    lb = SmoothWRR()
    out = []
    for raw in sys.stdin.read().splitlines():
        parts = raw.split()
        if not parts:
            continue
        cmd = parts[0]
        if cmd == 'POOL':
            lb.set_pool(parts[1:])
            out.append('OK')
        elif cmd == 'PICK':
            out.append(lb.pick())
        elif cmd == 'PICKN':
            n = int(parts[1])
            out.append(','.join(lb.pick() for _ in range(n)))
    sys.stdout.write(''.join(line + '\n' for line in out))


if __name__ == '__main__':
    main()
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
        if not self.names or self.W <= 0:
            return 'EMPTY'

        maxInd = -1

        # Step 1: Add each backend's weight.
        for i in range(len(self.weights)):
            self.current[i] += self.weights[i]

            # Step 2: Find the highest score.
            # Strict > preserves the earliest backend on ties.
            if self.weights[i] > 0 and (
                maxInd == -1 or self.current[i] > self.current[maxInd]
            ):
                maxInd = i

        # No backend has a positive weight.
        if maxInd == -1:
            return 'EMPTY'

        # Step 3: Penalize the winning backend.
        self.current[maxInd] -= self.W

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
import sys


class RoundRobin:
    def __init__(self):
        self.pool = []
        self.counter = 0

    def set_pool(self, names):
        self.pool = list(names)
        self.counter = 0

    def reset(self):
        self.counter = 0

    def pick(self):
        # TODO: return the backend at counter mod N, then advance the counter.
        # An empty pool answers 'EMPTY'.
        result  = 'EMPTY' if not self.pool else self.pool[self.counter % len(self.pool)]
        self.counter = (self.counter + 1) % len(self.pool) if self.pool else 0
        return result


def main():
    rr = RoundRobin()
    out = []
    for raw in sys.stdin.read().splitlines():
        parts = raw.split()
        if not parts:
            continue
        cmd = parts[0]
        if cmd == 'POOL':
            rr.set_pool(parts[1:])
            out.append('OK')
        elif cmd == 'PICK':
            out.append(rr.pick())
        elif cmd == 'RESET':
            rr.reset()
            out.append('OK')
    sys.stdout.write(''.join(line + '\n' for line in out))


if __name__ == '__main__':
    main()

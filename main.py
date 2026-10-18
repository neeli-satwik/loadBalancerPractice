import sys


class LeastConn:
    def __init__(self):
        self.pool = []
        self.active = {}
        self.n = 0

    def set_pool(self, names):
        self.pool = list(names)
        self.active = {n: 0 for n in self.pool}

    def done(self, name):
        if self.active.get(name, 0) > 0:
            self.active[name] -= 1

    def status(self):
        return ['%s:%d' % (n, self.active[n]) for n in sorted(set(self.pool))]

    def pick(self):
        # TODO: choose the backend with the fewest in-flight requests (the first one
        # in pool order wins a tie), count the request against it, and return its name.
        # An empty pool answers 'EMPTY'.
        if not self.active or self.n == 0:
            return 'EMPTY'

        for server in self.pool:
            if self.active[server] == min(self.active.values()):
                self.active[server] += 1
                return server


def main():
    lb = LeastConn()
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
        elif cmd == 'DONE':
            lb.done(parts[1])
            out.append('OK')
        elif cmd == 'STATUS':
            out.extend(lb.status())
    sys.stdout.write(''.join(line + '\n' for line in out))


if __name__ == '__main__':
    main()

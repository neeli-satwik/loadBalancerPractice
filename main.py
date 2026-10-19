import sys

MOD = 2 ** 31


class P2C:
    def __init__(self):
        self.pool = []
        self.active = {}
        self.state = 1

    def set_pool(self, names):
        self.pool = list(names)
        self.active = {n: 0 for n in self.pool}

    def draw(self):
        self.state = (self.state * 1103515245 + 12345) % MOD
        return self.state >> 16

    def done(self, name):
        if self.active.get(name, 0) > 0:
            self.active[name] -= 1

    def choose(self, a, b):
        # TODO: of the two named backends, pick the one with fewer in-flight requests
        # (a tie goes to the lexicographically smaller name), count the request
        # against it, and return its name.
        chosen = None
        if self.active[a]==self.active[b]: 
            chosen = a if a < b else b
        else:
            chosen = a if self.active[a] < self.active[b] else b
        self.active[chosen] += 1
        return chosen
        
    def sample(self):
        # TODO: PICK with no arguments. Empty pool -> 'EMPTY'; one backend -> choose it
        # without drawing; otherwise draw twice (i = draw mod n, j = draw mod (n - 1),
        # and if j >= i then j += 1) and choose between pool[i] and pool[j].
        if not self.pool:
            return 'EMPTY'
        if len(self.pool) == 1:
            self.active[self.pool[0]] += 1
            return self.pool[0]
        i = self.draw() % len(self.pool)
        j = self.draw() % (len(self.pool) - 1)
        if j >= i:
            j += 1
        chosen = self.choose(self.pool[i], self.pool[j])
        return chosen


def main():
    lb = P2C()
    out = []
    for raw in sys.stdin.read().splitlines():
        parts = raw.split()
        if not parts:
            continue
        cmd = parts[0]
        if cmd == 'POOL':
            lb.set_pool(parts[1:])
            out.append('OK')
        elif cmd == 'SEED':
            lb.state = int(parts[1]) % MOD
            out.append('OK')
        elif cmd == 'PICK':
            if len(parts) >= 3:
                a, b = parts[1], parts[2]
                if a in lb.active and b in lb.active:
                    out.append(lb.choose(a, b))
                else:
                    out.append('ERR')
            else:
                out.append(lb.sample())
        elif cmd == 'DONE':
            lb.done(parts[1])
            out.append('OK')
        elif cmd == 'STATUS':
            for n in sorted(lb.pool):
                out.append('%s:%d' % (n, lb.active[n]))
    sys.stdout.write(''.join(line + '\n' for line in out))


if __name__ == '__main__':
    main()


import sys

MOD = 2 ** 31


class P2C:
    def __init__(self):
        self.pool = []
        self.active = {}
        self.state = 1

    def set_pool(self, names):
        # Deduplicate while preserving the original order.
        self.pool = list(dict.fromkeys(names))
        self.active = {name: 0 for name in self.pool}

    def draw(self):
        # Keep the original PRNG exactly unchanged.
        self.state = (
            self.state * 1103515245 + 12345
        ) % MOD
        return self.state >> 16

    def done(self, name):
        # Unknown names and duplicate DONE calls are harmless.
        if self.active.get(name, 0) > 0:
            self.active[name] -= 1

    def choose(self, a, b):
        # Validate even when choose() is called directly.
        if a not in self.active or b not in self.active:
            return None

        # Fewer in-flight requests wins.
        # Ties are broken lexicographically.
        if self.active[a] <= self.active[b]:
            chosen = a
        else:
            chosen = b

        self.active[chosen] += 1
        return chosen

    def sample(self):
        n = len(self.pool)

        if n == 0:
            return 'EMPTY'

        if n == 1:
            # Must not consume PRNG draws.
            name = self.pool[0]
            self.active[name] += 1
            return name

        # Sample two distinct indices uniformly by this scheme.
        i = self.draw() % n
        j = self.draw() % (n - 1)

        if j >= i:
            j += 1

        return self.choose(self.pool[i], self.pool[j])


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
            if len(parts) != 2:
                out.append('ERR')
                continue

            try:
                lb.state = int(parts[1]) % MOD
                out.append('OK')
            except ValueError:
                out.append('ERR')

        elif cmd == 'PICK':
            if len(parts) == 1:
                out.append(lb.sample())

            elif len(parts) == 3:
                a, b = parts[1], parts[2]
                chosen = lb.choose(a, b)
                out.append(chosen if chosen is not None else 'ERR')

            else:
                out.append('ERR')

        elif cmd == 'DONE':
            if len(parts) != 2:
                out.append('ERR')
            else:
                lb.done(parts[1])
                out.append('OK')

        elif cmd == 'STATUS':
            if len(parts) != 1:
                out.append('ERR')
            else:
                for name in sorted(lb.pool):
                    out.append(
                        '{}:{}'.format(name, lb.active[name])
                    )

        else:
            out.append('ERR')

    sys.stdout.write(''.join(line + '\n' for line in out))


if __name__ == '__main__':
    main()

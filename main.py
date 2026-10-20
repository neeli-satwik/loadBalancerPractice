import sys

TRIP, COOLDOWN, CLOSE_AFTER = 5, 30, 3
DIGITS = '0123456789'


def status_code(tokens):
    """The status code of a well-formed status line, or -1 for anything else."""
    if len(tokens) < 2:
        return -1
    version, code = tokens[0], tokens[1]
    if len(version) != 8 or version[:5] != 'HTTP/' or version[5] not in DIGITS \
            or version[6] != '.' or version[7] not in DIGITS:
        return -1
    if len(code) != 3 or any(c not in DIGITS for c in code):
        return -1
    return int(code)


def is_error(tokens):
    code = status_code(tokens)
    return code < 0 or 500 <= code <= 599


class Breakers:
    def __init__(self):
        self.now = 0
        self.pool = []
        self.state = {}
        self.errors = {}
        self.good = {}
        self.opened = {}

    def set_pool(self, names):
        self.pool = list(names)
        self.state = {n: 'CLOSED' for n in self.pool}
        self.errors = {n: 0 for n in self.pool}
        self.good = {n: 0 for n in self.pool}
        self.opened = {n: 0 for n in self.pool}


    def state_of(self, name):
        self.refresh(name)
        return self.state[name]

    def refresh(self, name):
        if self.state[name] == 'OPEN' and self.now - self.opened[name] >= COOLDOWN:
            self.state[name] = 'HALF_OPEN'
            self.good[name] = 0
            self.errors[name] = 0

    def call(self, name, err):
        self.refresh(name)
        st = self.state[name]
        if st == 'OPEN':
            return 'SHORT'
        if st == 'CLOSED':
            if err:
                self.errors[name] += 1
                if self.errors[name] >= TRIP:
                    self.state[name] = 'OPEN'
                    self.opened[name] = self.now
                    self.errors[name] = 0
            else:
                self.errors[name] = 0
        else:  # HALF_OPEN
            if err:
                self.state[name] = 'OPEN'
                self.opened[name] = self.now
                self.good[name] = 0
            else:
                self.good[name] += 1
                if self.good[name] >= CLOSE_AFTER:
                    self.state[name] = 'CLOSED'
                    self.good[name] = 0
                    self.errors[name] = 0
        return 'ERROR' if err else 'OK'


def main():
    b = Breakers()
    out = []
    for raw in sys.stdin.read().splitlines():
        parts = raw.split()
        if not parts:
            continue
        cmd = parts[0]
        if cmd == 'POOL':
            b.set_pool(parts[1:])
            out.append('OK')
        elif cmd == 'NOW':
            b.now = int(parts[1])
            out.append('OK')
        elif cmd == 'CALL':
            if parts[1] not in b.state:
                out.append('ERR')
                continue
            out.append(b.call(parts[1], is_error(parts[2:])))
        elif cmd == 'STATUS':
            for n in b.pool:
                out.append('%s %s' % (n, b.state_of(n)))
    sys.stdout.write(''.join(line + '\n' for line in out))


if __name__ == '__main__':
    main()

import sys

FALL, RISE = 3, 2
DIGITS = '0123456789'


def probe_passes(tokens: list[str]) -> bool:
    """tokens: the answer split on whitespace, e.g. ['HTTP/1.1', '200', 'OK']."""
    # TODO: true only for a well-formed status line with a code from 200 to 399:
    #   tokens[0] is 'HTTP/' + digit + '.' + digit, tokens[1] is exactly three digits.
    # TIMEOUT, REFUSED and anything malformed fail.
    status = tokens[1] if len(tokens) > 1 else ''
    if status.isdigit() or (int(status) < 200 or int(status) > 399):
        return False
    return True


class Health:
    def __init__(self):
        self.pool = []
        self.up = {}
        self.fails = {}
        self.passes = {}

    def set_pool(self, names):
        self.pool = list(names)
        self.up = {n: True for n in self.pool}
        self.fails = {n: 0 for n in self.pool}
        self.passes = {n: 0 for n in self.pool}

    def record(self, name, ok):
        # TODO: update the two streaks for this backend and flip its state:
        #a pass clears the failure streak, a failure clears the pass streak;
        #UP -> DOWN at FALL consecutive failures, DOWN -> UP at RISE consecutive passes.
        if ok:
            self.fails[name] = 0
            self.passes[name] += 1
            if not self.up[name] and self.passes[name] >= RISE:
                self.up[name] = True
        else:
            self.passes[name] = 0
            self.fails[name] += 1
            if self.up[name] and self.fails[name] >= FALL:
                self.up[name] = False


def main():
    h = Health()
    out = []
    for raw in sys.stdin.read().splitlines():
        parts = raw.split()
        if not parts:
            continue
        cmd = parts[0]
        if cmd == 'POOL':
            h.set_pool(parts[1:])
            out.append('OK')
        elif cmd == 'PROBE':
            name = parts[1]
            if name not in h.up:
                out.append('ERR')
                continue
            ok = probe_passes(parts[2:])
            h.record(name, ok)
            out.append('PASS' if ok else 'FAIL')
        elif cmd == 'STATUS':
            for n in h.pool:
                out.append('%s %s' % (n, 'UP' if h.up[n] else 'DOWN'))
        elif cmd == 'HEALTHY':
            ups = [n for n in h.pool if h.up[n]]
            out.append(','.join(ups) if ups else 'none')
    sys.stdout.write(''.join(line + '\n' for line in out))


if __name__ == '__main__':
    main()

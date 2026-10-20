import sys

FALL, RISE, EJECT = 3, 2, 3
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


def probe_passes(tokens):
    code = status_code(tokens)
    return 200 <= code <= 399


def observe_is_error(tokens):
    # TODO: true when a REAL response counts against the backend: not a well-formed
    # status line (status_code gives -1), or a code from 500 to 599. 4xx is fine.
    status = status_code(tokens)
    if status == -1 or (500 <= status <= 599):
        return True
    return False


class Health:
    def __init__(self):
        self.pool = []
        self.active_up = {}
        self.fails = {}
        self.passes = {}
        self.errors = {}

    def set_pool(self, names):
        self.pool = list(names)
        self.active_up = {n: True for n in self.pool}
        self.fails = {n: 0 for n in self.pool}
        self.passes = {n: 0 for n in self.pool}
        self.errors = {n: 0 for n in self.pool}

    def probe(self, name, ok):
        if ok:
            self.passes[name] += 1
            self.fails[name] = 0
            if not self.active_up[name] and self.passes[name] >= RISE:
                self.active_up[name] = True
        else:
            self.fails[name] += 1
            self.passes[name] = 0
            if self.active_up[name] and self.fails[name] >= FALL:
                self.active_up[name] = False

    def observe(self, name, is_error):
        # TODO: an error adds one to this backend's passive streak, a fine response
        # sets the streak back to 0.
        if is_error:
            self.errors[name] += 1
        else:
            self.errors[name] = 0
        pass

    def is_up(self, name):
        # TODO: UP only if the active side is up AND the passive streak is below EJECT.
        return self.active_up[name] and self.errors[name] < EJECT


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
            if parts[1] not in h.active_up:
                out.append('ERR')
                continue
            ok = probe_passes(parts[2:])
            h.probe(parts[1], ok)
            out.append('PASS' if ok else 'FAIL')
        elif cmd == 'OBSERVE':
            if parts[1] not in h.active_up:
                out.append('ERR')
                continue
            err = observe_is_error(parts[2:])
            h.observe(parts[1], err)
            out.append('ERROR' if err else 'OK')
        elif cmd == 'STATUS':
            for n in h.pool:
                out.append('%s %s' % (n, 'UP' if h.is_up(n) else 'DOWN'))
    sys.stdout.write(''.join(line + '\n' for line in out))


if __name__ == '__main__':
    main()
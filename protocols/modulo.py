from protocol import Protocol
from transition import Transition

def name(a, c, m):
    return "Remainder ({}, {}, {})".format(a, c, m)

def generate(a, c, m):
    def var(i):
        return "x{}".format(i)

    numeric = range(m)
    boolean = ["t", "f"]

    Q = set(numeric) | set(boolean)
    S = {var(i) for i in range(len(a))}
    I = {var(i): a[i] % m for i in range(len(a))}
    O = {q: 1 if (q == c or q == "t") else 0 for q in Q}
    T = set()

    for n in numeric:
        for n_ in numeric:
            pre  = (n, n_)
            post = ((n + n_) % m, "t" if ((n + n_) % m) == c else "f")

            T.add(Transition(pre, post))

        for b in boolean:
            pre  = (n, b)
            post = (n, "t" if n == c else "f")
            
            T.add(Transition(pre, post))

    return Protocol(Q, T, S, I, O)

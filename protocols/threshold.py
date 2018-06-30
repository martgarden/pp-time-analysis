from protocol import Protocol
from transition import Transition

def name(a, c):
    return "Threshold ({}, {})".format(a, c)

def generate(a, c):
    v_max = max(max(abs(x) for x in a), c + 1)

    def f(x, y):
        return max(-v_max, min(v_max, x + y))

    def g(x, y):
        return (x + y) - f(x, y)

    def b(x, y):
        return (f(x, y) < c)

    def var(i):
        return "x{}".format(i)

    def label(q):
        return "{}{}({})".format("L" if q[0] else "P",
                                 "T" if q[2] else "F",
                                 q[1])

    Q = {(l, v, o) for l in [False, True] for v in range(-v_max, v_max+1)
                   for o in [False, True]}
    S = {var(i) for i in range(len(a))}
    I = {var(i): label((True, a[i], a[i] < c)) for i in range(len(a))}
    O = {label(q): 1 if q[2] else 0 for q in Q}
    T = set()

    for p in Q:
        for q in Q:
            if p[0]:
                n, n_ = p[1], q[1]
                pre   = (label(p), label(q))
                post  = (label((True,  f(n, n_), b(n, n_))),
                         label((False, g(n, n_), b(n, n_))))

                T.add(Transition(pre, post))

    Q = map(label, Q)

    return Protocol(Q, T, S, I, O)

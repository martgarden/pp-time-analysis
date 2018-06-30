from protocol import Protocol
from transition import Transition

def name(n):
    return "Flock-of-birds ({})".format(n)

def generate(n):
    Q = set(range(n + 1))
    T = set()
    S = {"0", "1"}
    I = {"0": 0, "1": 1}
    O = {i: (0 if i < n else 1) for i in Q}

    for i in range(n + 1):
        for j in range(n + 1):
            if i + j < n:
                T.add(Transition((i, j), (0, i + j)))
            else:
                T.add(Transition((i, j), (n, n)))

    return Protocol(Q, T, S, I, O)

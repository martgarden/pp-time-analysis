from protocol import Protocol
from transition import Transition

def name(n):
    return "Flock-of-birds 2 ({})".format(n)

# From https://hal.archives-ouvertes.fr/hal-00565090/document
# Example 2, p. 5
def generate(n):
    Q = set(range(n + 1))
    T = set()
    S = {"0", "1"}
    I = {"0": 0, "1": 1}
    O = {i: (0 if i < n else 1) for i in Q}

    for i in range(1, n):
        T.add(Transition((i, i), (i, i + 1)))

    for i in range(0, n):
        T.add(Transition((n, i), (n, n)))

    return Protocol(Q, T, S, I, O)

import math
from protocol import Protocol
from transition import Transition

def name(n):
    return "Flock-of-birds logarithmic ({})".format(n)

def generate(n):
    i = int(math.log(n, 2))
    states = [0] + [2**j for j in range(0, i + 1)]    
    cur_state = 2**i
    
    for j in range(i - 1, 0, -1):
        if n & 2**j:
            cur_state += 2**j
            states.append(cur_state)

    if n not in states:
        states.append(n)

    transitions = []

    for x in range(len(states)):
        for y in range(x, len(states)):
            q1 = states[x]
            q2 = states[y]
            tot  = q1 + q2
            pre  = (q1, q2)
            post = None

            if tot < n and q1 != 0 and q2 != 0 and tot in states:
                post = (tot, 0)
            elif tot >= n:
                post = (n, n)

            if post is not None:
                transitions.append(Transition(pre, post))

    Q = states
    T = transitions
    S = {"0", "1"}
    I = {"0": 0, "1": 1}
    O = {i: (0 if i < n else 1) for i in Q}

    return Protocol(Q, T, S, I, O)

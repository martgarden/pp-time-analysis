from protocol import Protocol
from transition import Transition

def name():
    return "Broadcast"

def generate():
    Q = {"t", "f"}
    T = {Transition(("t", "f"), ("t", "t"))}
    S = {"t", "f"}
    I = {"t": "t", "f": "f"}
    O = {"t": 1, "f": 0}

    return Protocol(Q, T, S, I, O)

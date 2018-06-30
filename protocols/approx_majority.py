from protocol import Protocol
from transition import Transition

def name():
    return "Approximate majority"

def generate():
    Q = {"Y", "N", "b"}
    T = {Transition(("Y", "b"), ("Y", "Y")),
         Transition(("Y", "N"), ("Y", "b")),
         Transition(("N", "Y"), ("N", "b")),
         Transition(("N", "b"), ("N", "N"))}
    S = {"Y", "N"}
    I = {"Y": "Y", "N": "N"}
    O = {"Y": 1, "N": 0, "b": 1}

    return Protocol(Q, T, S, I, O)

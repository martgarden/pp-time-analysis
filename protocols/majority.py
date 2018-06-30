from protocol import Protocol
from transition import Transition

def name():
    return "Majority"

def generate():
    Q = {"A", "B", "a", "b"}
    T = {Transition(("A", "B"), ("a", "b")),
         Transition(("A", "b"), ("A", "a")),
         Transition(("B", "a"), ("B", "b")),
         Transition(("a", "b"), ("b", "b"))}
    S = {"A", "B"}
    I = {"A": "A", "B": "B"}
    O = {"A": 0, "B": 1, "a": 0, "b": 1}

    return Protocol(Q, T, S, I, O)

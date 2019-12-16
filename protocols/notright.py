from protocol import Protocol
from transition import Transition

def name():
    return "Majority (no tie-breaker)"

def generate():
    Q = {"A", "B", "a", "b", "B'"}
    T = {Transition(("A", "B"), ("a", "b")),
         Transition(("A", "B'"), ("a", "b")),
         Transition(("A", "b"), ("A", "a")),
         Transition(("B", "a"), ("B", "b")),
         Transition(("B'", "a"), ("B'", "b")),
         Transition(("B", "B"), ("B'", "B'")),
         Transition(("B'", "B'"), ("B", "B")),
         Transition(("a", "b"), ("a", "a"))}
    S = {"A", "B"}
    I = {"A": "A", "B": "B"}
    O = {"A": 0, "B": 1, "a": 0, "b": 1, "B'":1}

    return Protocol(Q, T, S, I, O)

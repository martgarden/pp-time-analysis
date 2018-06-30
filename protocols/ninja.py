from protocol import Protocol
from transition import Transition

def name():
    return "Ninja"

def generate():
    Q = {"A", "B", "C", "a", "b"}
    T = {Transition(("A", "B"), ("b", "C")),
         Transition(("A", "C"), ("A", "a")),
         Transition(("B", "C"), ("B", "b")),
         Transition(("B", "a"), ("B", "b")),
         Transition(("A", "b"), ("A", "a")),
         Transition(("C", "a"), ("C", "b"))}
    S = {"A", "B"}
    I = {"A": "A", "B": "B"}
    O = {"A": 0, "B": 1, "C": 1, "a": 0, "b": 1}
    
    return Protocol(Q, T, S, I, O)

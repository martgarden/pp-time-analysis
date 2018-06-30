from protocol import Protocol
from transition import Transition

def name(m, d):
  return "Average-and-conquer ({}, {})".format(m, d)

def generate(m, d):
  # Generate states
  states = [("weak", ("+", 0)), ("weak", ("-", 0))]

  for n in range(3, m + 1, 2):
    states.append(("strong",  n))
    states.append(("strong", -n))

  for n in range(1, d + 1):
    states.append(("intermediate", ("+", n)))
    states.append(("intermediate", ("-", n)))

  # Helper functions
  def strong(x):
    return x[0] == "strong"

  def intermediate(x):
    return x[0] == "intermediate"

  def weak(x):
    return x[0] == "weak"

  def value(x):
    if strong(x):
      return x[1]
    elif intermediate(x):
      return 1 if x[1][0] == "+" else -1
    elif weak(x):
      return 0

  def weight(x):
    return abs(value(x))

  def sgn(x):
    if strong(x) or intermediate(x):
      return 1 if value(x) > 0 else -1
    else:
      return 1 if x[1][0] == "+" else -1

  def phi(r):
    if abs(r) > 1:
      return ("strong", r)
    else:
      return ("intermediate", ("+" if r > 0 else "-", 1))

  def r_down(k):
    r = k if abs(k) % 2 == 1 else k - 1

    return phi(r);

  def r_up(k):
    r = k if abs(k) % 2 == 1 else k + 1

    return phi(r)

  def shift_to_zero(x):
    if intermediate(x):
      j = x[1][1]

      if j < d:
        sign = "+" if value(x) == 1 else "-"

        return ("intermediate", (sign, j + 1))

    return x

  def sign_to_zero(x):
    sign = "+" if sgn(x) > 0 else "-"

    return ("weak", (sign, 0))

  def update(x, y):
    if ((weight(x) > 0 and weight(y) > 1) or (weight(y) > 0 and weight(x) > 1)):
      x_ = r_down((value(x) + value(y)) // 2)
      y_ =   r_up((value(x) + value(y)) // 2)
    elif (weight(x) * weight(y) == 0 and value(x) + value(y) != 0):
      if weight(x) != 0:
        x_ = shift_to_zero(x)
        y_ =  sign_to_zero(x)
      else:
        y_ = shift_to_zero(y)
        x_ =  sign_to_zero(y)
    elif ((intermediate(x) and x[1][1] == d and weight(y) and sgn(x) != sgn(y)) or
          (intermediate(y) and y[1][1] == d and weight(x) and sgn(y) != sgn(x))):
      x_ = ("weak", ("-", 0))
      y_ = ("weak", ("+", 0))
    else:
      x_ = shift_to_zero(x)
      y_ = shift_to_zero(y)

    return (x_, y_)

  def state_repr(x):
    sign = "G" if sgn(x) > 0 else "B"

    if strong(x):
      return "{}{}".format(sign, weight(x))
    elif intermediate(x):
      return "{}1_{}".format(sign, x[1][1])
    else:
      return "{}0".format(sign)

  def pair_repr(pair):
    return map(state_repr, pair)

  def generate_states():
    return map(state_repr, states)

  def generate_transitions():
    transitions = []

    for x in range(0, len(states)):
      for y in range(x, len(states)):
        p = states[x]
        q = states[y]
        pre  = pair_repr((p, q))
        post = pair_repr(update(p, q))

        transitions.append(Transition(pre, post))

    return transitions

  def generate_initial_states():
    return ["G{}".format(m), "B{}".format(m)]

  def generate_output_mapping():
    out = {}
    
    for q in states:
      out[state_repr(q)] = 1 if sgn(q) == 1 else 0
        
    return out

  Q = generate_states()
  T = generate_transitions()
  S = generate_initial_states()
  I = {q: q for q in S}
  O = generate_output_mapping()
  
  return Protocol(Q, T, S, I, O)

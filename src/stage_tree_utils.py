# -*- coding: utf-8 -*-
from graph_tool.draw import graphviz_draw
from stage_utils import Speed

def pretty_speed(speed):
    labels = {None: "?",
              Speed.ZERO: "0",
              Speed.QUADRATIC: "n²",
              Speed.QUADRATIC_LOG: "n²·log(n)",
              Speed.CUBIC: "n³",
              Speed.POLYNOMIAL: "poly(n)",
              Speed.EXPONENTIAL: "n⁰⁽ⁿ⁾"}

    return labels[speed]
    
def pretty_valuation(valuation):
    pos = []
    neg = []
 
    for var in valuation:
        if ((valuation[var] is True) and
            (var.unique or (not var.unique and
                            valuation[var.opposite()] is not True))):
            pos.append(var)
        elif ((valuation[var] is False) and
              (not var.unique or (var.unique and
                                  valuation[var.opposite()] is not False))):
            neg.append(var)
        
    elems = sorted(map(str, pos)) + sorted(map(lambda v: "¬" + str(v), neg))
    lines = []
    NUM   = 5

    for i in range((len(elems) + NUM - 1) // NUM):
        lines.append(", ".join(elems[NUM*i:NUM*i + NUM + 1]))

    return "[" + "\n".join(lines) + "]"

def pretty_pairs(pairs):
    if len(pairs) == 0:
        return "∅"
    else:
        return "{" + ", ".join(("".join(str(q) for q in pair)) for
                               pair in pairs) + "}"

def pretty_stage(stage):
    valuations = stage.formula.solutions()
    sol = []
    
    for v in valuations:
        sol.append(pretty_valuation(v))
        
    acc  = "Sol(Φ) =\n[" + ";\n".join(sol) + "]"
    acc += "\n\nπ =\n" + pretty_valuation(stage.valuation)
    acc += "\n\nT =\n" + pretty_pairs(stage.disabled)
    
    return acc

def export(tree, filename, struct_only=False):
    SIZE = (200, 150)
    FONT_SIZE = 40.0
    
    labels = tree.graph.new_vertex_property("string")
    colors = tree.graph.new_vertex_property("string")
    speed  = tree.graph.new_edge_property("string")
    
    for i in tree.stages:
        labels[i] = pretty_stage(tree.stages[i])
        colors[i] = "deepskyblue1" if (i in tree.leaves) else "azure2"

    for e in tree.graph.edges():
        _, j = e
        speed[e] = " " + pretty_speed(tree.stages[j].speed)

    if not struct_only:
        graphviz_draw(tree.graph, layout="dot",
                      vprops={"label": labels, "fillcolor": colors,
                              "fontsize": FONT_SIZE},
                      eprops={"label": speed, "fontsize": FONT_SIZE},
                      output=filename, size=SIZE, ratio="auto")
    else:
        graphviz_draw(tree.graph, layout="dot",
                      vprops={"fillcolor": colors},
                      output=filename, size=SIZE, ratio="auto")

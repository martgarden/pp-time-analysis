# -*- coding: utf-8 -*-
import argparse
import importlib.util
import json
import sys

sys.path.append("../src/")

def pretty_speed(speed):
    labels = {None: "?",
              "Speed.ZERO": "$0$",
              "Speed.QUADRATIC": "$n^2$",
              "Speed.QUADRATIC_LOG": "$n^2 \\cdot \\log n$",
              "Speed.CUBIC": "$n^3$",
              "Speed.POLYNOMIAL": "$\\mathrm{poly}(n)$",
              "Speed.EXPONENTIAL": "$\\mathrm{exp}(n)$"}

    return labels[speed]

def load_protocol(protocol):
    filename = protocol[0]
    args     = json.loads(protocol[1]) if len(protocol) > 1 else []

    spec = importlib.util.spec_from_file_location("", filename)
    gen  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)

    return (gen.name(*args), gen.generate(*args))

def table(data):
    TEMPLATE = "  {:28} & {:3} & {:3} & {:3} & {:3} & {:3} & {:18} & {:5} \\\\"

    print("\\begin{tabular}{|l|r|r|c|c|c|c|r|}")
    print("  \\hline")
    print(TEMPLATE.format("Protocol", "$|Q|$", "$|T|$",
                          "Stages", "Leaves", "Max depth", "Bound", "Time"))
    print("  \\hline")
    
    for d in data:
        name, protocol = load_protocol(d["protocol"])
        
        if d["elapsed"]["tree"] != "timeout":
            stages   = d["tree"]["stages"]
            leaves   = d["tree"]["leaves"]
            depth    = d["tree"]["max-depth"]
            speed    = pretty_speed(d["tree"]["speed"])
            duration = "{:.3f}".format(d["elapsed"]["tree"])
        else:
            stages   = "---" 
            leaves   = "---"
            depth    = "---"
            speed    = "---"
            duration = "timeout"
            
        print(TEMPLATE.format(name,
                              len(protocol.states), len(protocol.transitions),
                              stages, leaves, depth, speed, duration))

    print("  \\hline")
    print("\\end{tabular}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()    

    parser.add_argument("data", metavar="data", type=str,
                        help=("benchmarks data filename"))

    args = parser.parse_args()

    with open(args.data) as data_file:
        data = json.load(data_file)
 
    table(data)

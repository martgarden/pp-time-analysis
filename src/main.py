# -*- coding: utf-8 -*-
import argparse
import importlib.util
import json
import time

from stage_tree import StageTree
from stage_tree_utils import export

DESCRIPTION = ("Automatic analysis of expected termination time "
               "of population protocols.")

verbose = False

def log(message):
    if verbose:
        print(message)

def load_protocol(filename, args):
    log("Loading protocol from {}...".format(filename))
    
    spec = importlib.util.spec_from_file_location("", filename)
    gen  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    protocol = gen.generate(*args)

    log(("Protocol loaded "
         "({} states, {} transitions).").format(len(protocol.states),
                                                len(protocol.transitions)))

    return protocol

def generate_tree(protocol):
    log("Generating stage tree...")

    tree = StageTree(protocol)

    log("Stage tree generated. ")
    log("Generated {} stages and {} leaves.".format(len(tree.stages),
                                                    len(tree.leaves)))

    return tree

def export_tree(tree, filename, struct_only):
    log("Exporting stage tree...")
    export(tree, filename=filename, struct_only=struct_only)
    log("Stage tree exported to {}.".format(filename))

def execute(args):
    global verbose
    verbose = args.verbose

    start     = time.process_time()
    prot_args = json.loads(args.protocol[1]) if len(args.protocol) > 1 else []
    protocol  = load_protocol(args.protocol[0], prot_args)
    end       = time.process_time()
    load_time = end - start

    log("Loading took {:.4f} seconds.".format(load_time))

    start     = time.process_time()
    tree      = generate_tree(protocol)
    end       = time.process_time()
    tree_time = end - start

    log("Generation took {:.4f} seconds.".format(tree_time))

    # Create outputs
    output = {}
    output["elapsed"]  = {"loading": load_time, "tree": tree_time}
    output["tree"] = {"stages": len(tree.stages), "leaves": len(tree.leaves),
                      "speed": str(tree.speed), "max-depth": tree.max_depth()}

    if args.tree is not None:
        export_tree(tree, args.tree[0], args.struct)

    return json.dumps(output) if args.out else None

if __name__ == "__main__":
    # Create parser and parse arguments
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    
    parser.add_argument("protocol", metavar="protocol", nargs="+", type=str,
                        help=("protocol filename and "
                               "optional arguments as JSON list"))
    parser.add_argument("-t", "--tree", metavar="filename", nargs=1, type=str,
                        help="export stage tree to filename")
    parser.add_argument("-o", "--out",
                        help="output results", action="store_true")
    parser.add_argument("-v", "--verbose",
                        help="enable verbosity", action="store_true")
    parser.add_argument("-s", "--struct",
                        help="generate only stage tree structure (no labels)",
                        action="store_true")

    args = parser.parse_args()
    out  = execute(args)

    if out is not None:
        print(out)

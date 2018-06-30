This tool analyzes the expected termination time of population protocols. It takes as input a population protocol and outputs a parametric upper bound on its expected termination time. The tool is a prototype of the algorithm described in:

Michael Blondin, Javier Esparza and Antonín Kučera. Automatic Analysis of Expected Termination Time for Population Protocols. Proc. 29th International Conference on Concurrency Theory (CONCUR), 2018.

## Installation

The tool requires Python ≥3.6 and the following dependencies:

- z3
- graph_tool

**z3** is available at https://github.com/Z3Prover/z3 and works on the major operating systems. It can, e.g., be installed as follows:

- Ubuntu: sudo apt-get install z3
- OS X: brew install z3

You may have to install the Python bindings: https://github.com/Z3Prover/z3#python.

**graph_tool** is available at https://graph-tool.skewed.de and works on most Linux distributions and OS X. Follow these installation instructions: https://git.skewed.de/count0/graph-tool/wikis/installation-instructions.

## Usage

The tool can be used by running

```
python3 src/main.py protocols/majority.py -ov
```

If a protocol requires some arguments, then they can be passed in the JSON format. For example,

```
python3 src/main.py protocols/modulo.py "[[1, 2], 0, 3]" -ov
```

for modulo([1, 2], 0, 3).

The flag -o outputs statistics in the JSON format. The -v flag outputs the progress of the execution. The stage tree can also be generated as a PDF as follows:

```
python3 src/main.py protocols/majority.py -t tree.pdf
```

If the tree is too large, it is possible to only generate its structure:

```
python3 src/main.py protocols/majority.py -s -t tree.pdf
```

For the list of possible arguments, run:

```
python3 src/main.py -h
```

## Benchmarks

The instructions regarding benchmarking can be found in ./benchmarks.

## Protocols

Protocols can be specified as simple Python scripts. Many examples are given in ./protocols and can serve as a basis to add more protocols.

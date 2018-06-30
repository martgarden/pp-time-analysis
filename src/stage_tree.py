from graph_tool import Graph
from graph_tool.topology import shortest_distance
from formula import Formula
from speed import Speed
from stage import Stage
from stage_utils import new_stage
from valuation import Valuation

class StageTree:
    def __init__(self, protocol):
        self._protocol = protocol
        self._graph    = Graph(directed=True)
        self._vertices = {}
        self._leaves   = set()
        self._speed    = Speed.ZERO
        self._construct_tree()

    def _construct_tree(self):
        def add_vertex(stage):
            vertex = self._graph.add_vertex()
            index  = self._graph.vertex_index[vertex]

            self._vertices[index] = stage

            return index
            
        root_formula = Formula()
        root_formula.assert_some_states_present(self._protocol.initial_states)
        root_formula.assert_all_states_absent(self._protocol.states -
                                              self._protocol.initial_states)

        root_stage = Stage(root_formula, Valuation(), set(), speed=Speed.ZERO)
        root_index = add_vertex(root_stage)
        unexplored = [(root_index, root_stage)]
        mem = {} # for memoization in computation of J

        while len(unexplored) > 0:
            index, stage = unexplored.pop()
            valuations   = stage.formula.solutions()
            has_children = False
            
            for val in valuations:
                child_stage = new_stage(self._protocol, stage, val, mem)
            
                if not child_stage.is_redundant():
                    child_index = add_vertex(child_stage)
                    self._graph.add_edge(index, child_index)
                    unexplored.append((child_index, child_stage))
                    has_children = True
            
            if not has_children:
                self._leaves.add(index)

            self._speed = max(self._speed, stage.speed)

    @property
    def protocol(self):
        return self._protocol

    @property
    def graph(self):
        return self._graph

    @property
    def stages(self):
        return self._vertices

    @property
    def leaves(self):
        return self._leaves

    @property
    def speed(self):
        return self._speed

    def max_depth(self):
        return max(shortest_distance(self._graph,
                                     source=self._graph.vertex(0)))

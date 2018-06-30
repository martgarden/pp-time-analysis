import z3
from variable import Var
from valuation import Valuation

class Formula:
    def __init__(self, valuation=None, disabled=None):
        self._domain = set()
        self._assertions = []

        if valuation is not None:
            self.assert_valuation(valuation)

        if disabled is not None:
            self.assert_all_pairs_absent(disabled)

    @property
    def domain(self):
        return self._domain

    def __iter__(self):
        for v in self.domain:
            yield v

    @staticmethod
    def _id(var):
        return z3.Bool("{}{}".format(var.state,
                                     "!" if var.unique else ""))

    @staticmethod
    def _states_constraints(states):
        conjuncts = []
        domain    = set()

        for q in states:
            var = Var(q)
            
            conjuncts.append(z3.Not(Formula._id(var)))
            domain.add(var)

        return (z3.And(conjuncts), domain)
            
    def assert_some_states_present(self, states):
        constraints, domain = Formula._states_constraints(states) 
            
        self._assertions.append(z3.Not(constraints))
        self._domain |= domain

    def assert_all_states_absent(self, states):
        constraints, domain = Formula._states_constraints(states) 
            
        self._assertions.append(constraints)
        self._domain |= domain

    def assert_valuation(self, valuation):
        for var in valuation:
            self._domain.add(var)
            
            if valuation[var]:
                self._assertions.append(Formula._id(var))
            else:
                self._assertions.append(z3.Not(Formula._id(var)))
                
    @staticmethod
    def _pairs_constraints(pairs):
        conjuncts = []
        domain    = set()

        for pair in pairs:
            p, q = tuple(pair)

            if p != q:
                domain |= {Var(p), Var(q)}
                conjuncts.append(z3.Or(z3.Not(Formula._id(Var(p))),
                                       z3.Not(Formula._id(Var(q)))))
            else:
                domain |= {Var(p), Var(p, True)}
                conjuncts.append(z3.Or(z3.Not(Formula._id(Var(p))),
                                              Formula._id(Var(p, True))))
                      
        return (z3.And(conjuncts), domain)

    def _consistency_constraints(self):
        conjuncts = []
        
        for v in self._domain:
            if (v.unique):
                expr = z3.Implies(Formula._id(v),
                                  Formula._id(v.opposite()))
            else:
                expr = z3.Implies(z3.Not(Formula._id(v)),
                                  z3.Not(Formula._id(v.opposite())))

            conjuncts.append(expr)

        return z3.And(conjuncts)

    def assert_all_pairs_absent(self, pairs):
        constraints, domain = Formula._pairs_constraints(pairs)

        self._assertions.append(constraints)
        self._domain |= domain
                      
    def assert_some_pair_present(self, pairs):
        constraints, domain = Formula._pairs_constraints(pairs)

        self._assertions.append(z3.Not(constraints))
        self._domain |= domain

    def tautology_check(self, constraints):
        solver = z3.Solver()

        solver.add(self._consistency_constraints())
        solver.add(self._assertions)
        
        disjuncts = []

        for (pos, neg, pre) in constraints:
            absent, _ = Formula._pairs_constraints({pre})

            pos_conj = z3.And([Formula._id(v) for v in pos])
            neg_conj = z3.And([z3.Not(Formula._id(v)) for v in neg])
            
            disjuncts.append(z3.And(pos_conj, neg_conj, z3.Not(absent)))

        solver.add(z3.Or(disjuncts))
        
        result = solver.check()
        
        return (result == z3.unsat)

    def implies_all_absent_tautology_check(self, pairs):
        solver = z3.Solver()
        constraints, _ = Formula._pairs_constraints(pairs)

        solver.add(self._consistency_constraints())
        solver.add(z3.Not(z3.Implies(z3.And(self._assertions), constraints)))

        result = solver.check()
        
        return (result == z3.unsat)

    def implies_some_present_tautology_check(self, pairs):
        solver = z3.Solver()
        constraints, _ = Formula._pairs_constraints(pairs)

        solver.add(self._consistency_constraints())
        solver.add(self._assertions) # (assertions and constraints) equiv. to:
        solver.add(constraints)      # not(assertions => not constraints)

        result = solver.check()
        
        return (result == z3.unsat)

    def solutions(self):
        solver = z3.Solver()
        solver.add(self._consistency_constraints())
        solver.add(self._assertions)
        
        sol = []

        while (solver.check() == z3.sat):
            model = solver.model()
            valuation = Valuation()

            for var in self:
                valuation[var] = z3.is_true(model[Formula._id(var)])

            sol.append(valuation)

            # Forbid solution in future checks
            solver.add(z3.Or([z3.Not(Formula._id(v)) if valuation[v]
                              else Formula._id(v) for v in valuation]))

        return sol

    def implies(self, formula):
        solver = z3.Solver()

        solver.add(self._consistency_constraints())
        solver.add(formula._consistency_constraints())
        solver.add(z3.Not(z3.Implies(z3.And(self._assertions),
                                     z3.And(formula._assertions))))

        result = solver.check()
        
        return (result == z3.unsat)
                
    def __str__(self):
        return str(self._assertions)
                      
    def __repr__(self):
        return str(self)

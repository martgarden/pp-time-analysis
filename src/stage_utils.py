from graph_tool import Graph
from graph_tool.topology import label_components
from graph_tool.topology import shortest_distance
from formula import Formula
from speed import Speed
from stage import Stage
from valuation import Valuation
from variable import Var

def is_stable_or_dead(protocol, valuation, disabled):
    # Dead?
    dead = True
    
    for t in protocol.transitions:
        p, q = tuple(t.pre)
        
        if (not t.silent() and (t.pre not in disabled) and
            (valuation[Var(p)] is not False) and
            (valuation[Var(q)] is not False)):
            dead = False
            break

    if dead:
        return True

    # Stable?
    V = protocol.states - valuation.absent_states()
    out = {protocol.output(q) for q in V}

    if len(out) > 1:
        return False
    else:
        x = out.pop()
        R = set()

        for t in protocol.transitions:
            for q in t.post:
                if protocol.output(q) != x:
                    R.add(t.pre)

        formula = Formula(valuation, disabled)

        return formula.implies_all_absent_tautology_check(R)

def new_stage_valuation(protocol, valuation, disabled):
    def f(M, N):
        M_, N_ = set(M), set(N)

        def cannot_occur(t):
            return (len(t.preset & M) > 0 or (t.pre in disabled) or
                    (len(t.preset) == 1 and t.pre.some() in N))
        
        for q in M:
            T = {t for t in protocol.transitions if q in t.post}
            to_remove = any(not cannot_occur(t) for t in T)
            
            if to_remove:
                M_.remove(q)

        for q in N:
            S = {t for t in protocol.transitions if (q in t.pre)
                 and (t.pre.other(q) != q) and (not t.unchanged(q))}
            T = {t for t in protocol.transitions if q not in t.pre}

            to_remove = any(not((t.pre.other(q) in M) or (t.pre in disabled))
                            for t in S)
            to_remove = to_remove or any(not cannot_occur(t) for t in T)
            
            if to_remove:
                N_.remove(q)

        return (M_, N_)

    # Compute greatest fixed point (M, N) of f
    M,  N  = valuation.absent_states(), valuation.unique_states()
    M_, N_ = f(M, N)

    while (M, N) != (M_, N_):
        M,  N  = M_, N_
        M_, N_ = f(M, N)

    # Compute E
    E = set()
    P = valuation.present_states()

    for q in P:
        T = {t for t in protocol.transitions if (q in t.pre and
                                                 q not in t.post)}

        if all((t.pre.other(q) in M) or (t.pre in disabled)
               or (t.pre.other(q) == q and q in N) for t in T):
            E.add(q)

    # Construct new valuation
    new_valuation = Valuation()

    for q in M: new_valuation[Var(q)] = False
    for q in E: new_valuation[Var(q)] = True
    for q in N: new_valuation[Var(q, True)] = True

    return new_valuation

def transformation_graph(protocol, valuation, disabled, stable=False):
    V = protocol.states - valuation.absent_states()
    T = {t for t in protocol.transitions if (not t.silent()) and
         (t.preset <= V) and (t.postset <= V) and (t.pre not in disabled)}

    graph    = Graph(directed=True)
    vertices = {v: i for (i, v) in enumerate(V)}
    edges    = dict()

    def add_edge(p, q, t):
        graph.add_edge(vertices[p], vertices[q])

        if (p, q) in edges:
            edges[p, q].add(t)
        else:
            edges[p, q] = {t}
            
    graph.add_vertex(len(V))

    for t in T:
        common_states = t.preset & t.postset

        # Case: AB -> AC, AA -> AC, AB -> AA
        if len(common_states) == 1:
            p  = tuple(common_states)[0]
            q  = t.pre.other(p)
            q_ = t.post.other(p)

            if not stable or valuation[Var(p)] is True:
                add_edge(q, q_, t)
        # Case: AA -> BB, AA -> BC, AB -> CC, AB -> CD
        elif len(common_states) == 0:
            if stable:
                continue
            new_edges = {(p, q) for p in t.preset for q in t.postset}

            for (p, q) in new_edges:
                p_ = t.pre.other(p)
                
                if not stable or valuation[Var(p_)] is True:
                    add_edge(p, q, t)

    return (graph, vertices, edges,V)

def exp(protocol, valuation, disabled):
    graph, vertices, edges,V = transformation_graph(protocol, valuation,
                                                  disabled)
    components, _ = label_components(graph)
    expF = set()

    for (p, q) in edges:
        if components[vertices[p]] != components[vertices[q]]:
            for t in edges[p, q]:
                expF.add(t.pre)

    return (expF,graph,vertices,edges,V)

def larger(distance, vertices, r,s,p,q):
    maxint = 100000
    if (distance[vertices[r]][vertices[p]] < maxint) and (distance[vertices[s]][vertices[p]] < maxint):
        return True
    if (distance[vertices[r]][vertices[q]] < maxint) and (distance[vertices[s]][vertices[q]] < maxint):
        return True
    return False

def strictly_larger(distance, vertices,r,s,p,q):
    return larger(distance, vertices, r,s,p,q) and (not larger(distance, vertices,p,q,r,s))

def nextH(M,dF,distance,vertices):
    for t in dF:
        (p,q) = t
        addit = True
        for (r,s) in dF:
            if strictly_larger(distance, vertices, r,s,p,q):
                addit = False
                break
        if addit:
            M.add(t)
    return M

def compute_J(protocol, valuation, disabled, F, mem, graph, vertices):
    key = (valuation, frozenset(disabled))
    
    if key in mem:
        return mem[key]

    newM = set()
    M = set()
    sF = set(F)
    distance = shortest_distance(graph,directed=True)
    while not(len(newM) == len(sF)):
        newM = nextH(newM,sF.difference(newM),distance,vertices)
        M = newM
        stable = (len(M) == 0)

        while not stable:
            to_remove = set()
        
            for pair in M: # AB
                constraints = []
                
                for t in protocol.transitions:
                    if (t.post == pair):
                        constraints.append(([], [], t.pre))
                    elif len(set(pair) & t.postset) == 1:
                        p  = tuple(set(pair) & t.postset)[0] # E
                        q  = pair.other(p)                   # F
                        q_ = t.post.other(p)                 # G

                        if (q_ != q): # G != F
                            if p != q: # E != F
                                constraints.append(([Var(q)], [Var(p)], t.pre))
                            elif p not in t.pre: # E = F and E not in AB
                                constraints.append(([Var(p, True)], [], t.pre))
                                
                formula = Formula(valuation, disabled | M)

                if not formula.tautology_check(constraints):
                    to_remove.add(pair)

            if len(to_remove) > 0:
                M -= to_remove
            else:
                stable = True
        if len(M) > 0:
            break

    mem[key] = M
    
    return M

def eventually_disabled(protocol, valuation, disabled, mem):
    expF,graph,vertices,edges,V = exp(protocol, valuation, disabled)
    F    = set(expF)
    J    = compute_J(protocol, valuation, disabled, F, mem, graph, vertices)

    # while len(J) == 0 and len(expF) > 0:
    #     expF = exp(protocol, valuation, disabled | F)
    #     F   |= expF 
    #     J    = compute_J(protocol, valuation, disabled, F, mem)

    return F, J,graph,vertices,edges,V

def v_disabled(pairs, valuation):
    for pair in pairs:
        p, q = tuple(pair)

        if ((p != q and not(valuation[Var(p)] is False or
                            valuation[Var(q)] is False)) or
            (p == q and not(valuation[Var(p)] is False or
                            valuation[Var(p, True)] is True))):
            return False

    return True

def v_enabled(pairs, valuation):
    for pair in pairs:
        p, q = tuple(pair)

        if ((p != q and (valuation[Var(p)] is True and
                         valuation[Var(q)] is True)) or
            (p == q and (valuation[Var(p)] is True and
                         valuation[Var(p, True)] is False))):
            return True

    return False

def posts_from_pres(protocol, valuation, pres):
    V = protocol.states - valuation.absent_states()
    posts = set()
    
    for t in protocol.transitions:
        if (t.preset <= V) and (t.postset <= V) and (t.pre in pres):
            posts.add(t.post)

    return posts

def compute_I(protocol, valuation, disabled):
    graph, vertices, _, _ = transformation_graph(protocol, valuation,
                                              disabled, stable=True)
    components, _, is_bottom = label_components(graph, attractors=True)

    return {q for q in vertices if not is_bottom[components[vertices[q]]]}

def compute_L(protocol, valuation, disabled, I):
    V = protocol.states - valuation.absent_states()
    L = set()

    for t in protocol.transitions:
        take = (t.preset <= V) and (t.postset <= V)
        take = take and (t.pre not in disabled)
        take = take and (len(t.preset & I) > 0) and (len(t.postset & I) == 0)
        take = take and (len(t.preset) != 1 or
                         valuation[Var(t.pre.some(), True)] is not True)

        if take:
            L.add(t.post)

    return L

def is_small(protocol, valuation, disabled, J,graph,vertices,edges,V):
    emptycommons = True
    lV = list(V)
    for (p,q) in J:
        if(graph.vertex(vertices[p]).in_degree() > 0):
            return False, False
        if(graph.vertex(vertices[q]).in_degree() > 0):
            return False, False
        for (r,s) in graph.get_out_edges(vertices[p]):
            for t in edges[lV[r],lV[s]]:
                if len(t.preset & t.postset) > 0:
                    emptycommons = False
        for (r,s) in graph.get_out_edges(vertices[q]):
            for t in edges[lV[r],lV[s]]:
                if len(t.preset & t.postset) > 0:
                    emptycommons = False
    return True, emptycommons

def is_fast(protocol, valuation, disabled):
    graph, vertices, edges, _ = transformation_graph(protocol, valuation,
                                                  disabled)
    components, _, is_bottom = label_components(graph, attractors=True)

    U = {q for q in vertices if not is_bottom[components[vertices[q]]]}
    R = {q: set() for q in vertices}
    expV = set()

    for (p, q) in edges:
        if components[vertices[p]] != components[vertices[q]]:
           for t in edges[p, q]:
               expV.add(t.pre)
               
               if t.pre not in disabled:
                   for r in (set(t.pre) & U):
                       R[r].add(t.pre)
    
    for q in U:
        formula = Formula(valuation, disabled)
        formula.assert_some_pair_present(expV)
        formula.assert_some_states_present({q})
        
        if not formula.implies_some_present_tautology_check(R[q]):
            return False

    return True

def is_very_fast(protocol, valuation, disabled):
    graph, vertices, edges,_ = transformation_graph(protocol, valuation,
                                                  disabled)
    components, _, is_bottom = label_components(graph, attractors=True)

    U = {q for q in vertices if not is_bottom[components[vertices[q]]]}
    formula = Formula(valuation, disabled)
    
    for t in protocol.transitions:
        p,  q  = tuple(t.pre)
        p_, q_ = tuple(t.post)

        if (p  in vertices and q  in vertices and
            p_ in vertices and q_ in vertices and len({p, q, p_, q_} & U) > 0):
            if ((components[vertices[p]] != components[vertices[p_]]) and
                (components[vertices[p]] != components[vertices[q_]]) and
                (components[vertices[q]] != components[vertices[p_]]) and
                (components[vertices[q]] != components[vertices[q_]])):
                continue
            elif formula.implies_all_absent_tautology_check({t.pre}):
                continue
            else:
                return False

    return True

def new_stage(protocol, stage, valuation, mem):
    new_valuation = new_stage_valuation(protocol, valuation, stage.disabled)

    if is_stable_or_dead(protocol, new_valuation, stage.disabled):
        return Stage(Formula(new_valuation), new_valuation, stage.disabled,
                     speed=Speed.ZERO, parent=stage)

    F, J, graph, vertices, edges,V = eventually_disabled(protocol, new_valuation, stage.disabled, mem)

    # Compute new_formula (Φ) and new_disabled (T)
    if len(F) > 0:
        if len(J) > 0:
            new_disabled = set(stage.disabled) | set(J)
            new_formula  = Formula(new_valuation, new_disabled)

            if v_disabled(J, valuation):
                new_formula.assert_valuation(valuation)
            elif v_enabled(J, valuation):
                K = posts_from_pres(protocol, new_valuation, J)
                new_formula.assert_some_pair_present(K)

            # Compute speed
            if is_very_fast(protocol, new_valuation, stage.disabled):
                new_speed = Speed.QUADRATIC
            elif is_fast(protocol, new_valuation, stage.disabled):
                new_speed = Speed.QUADRATIC_LOG
            else:
                new_speed = Speed.CUBIC
            small, emptycommons = is_small(protocol, new_valuation, stage.disabled, J, graph, vertices, edges,V)
            if small and emptycommons:
                new_speed = Speed.QUADRATIC
            elif small and (not(new_speed == Speed.QUADRATIC)):
                new_speed = Speed.QUADRATIC_LOG
        else:
            new_disabled = set(stage.disabled) | set(F)
            new_formula  = Formula(new_valuation, new_disabled)
            new_speed    = Speed.POLYNOMIAL
    else:
        new_disabled = set(stage.disabled)
        new_formula  = Formula(new_valuation, new_disabled)
        new_speed    = Speed.EXPONENTIAL

        I = compute_I(protocol, new_valuation, stage.disabled)

        if any(valuation[Var(q)] is True for q in I):
            L = compute_L(protocol, new_valuation, stage.disabled, I)

            new_formula.assert_all_states_absent(I)
            new_formula.assert_some_pair_present(L)
        elif all(valuation[Var(q)] is False for q in I):
            new_formula.assert_valuation(valuation)
        else:
            new_formula.assert_all_states_absent(I)

    return Stage(new_formula, new_valuation, new_disabled,
                 speed=new_speed, parent=stage)

import networkx as nx
nil = lambda: None
guard = lambda x: nil if x is None else x
def to_graph(extracted, tier=None, display_opt=False):
    graph = nx.Graph()
    # TODO: handle PRPs separately
    if tier == 1.1:
        sbj = extracted[0]
        if not display_opt:
            sbj = EC.Entity(sbj[0], tag=sbj[1])
        else:
            sbj = sbj[0]
        pdt = extracted[1]
        if display_opt:
            pdt = pdt[0]
        obj = guard(extracted[2])
        if not display_opt:
            obj = EC.Entity(obj[0], tag=obj[1])
        else:
            obj = obj[0]
        graph.add_edge(sbj, obj, object=pdt)
    elif tier == 1.2:
        sbj = extracted[2]
        if not display_opt:
            sbj = EC.Entity(sbj[0], tag=sbj[1])
            sbj.dt = extracted[0]
            sbj.all = extracted[1]
            for attr in extracted[1]:
                setattr(sbj, attr[0], None)  # leave this empty for now ...
        else:
            sbj = sbj[0]
        pdt = extracted[3]
        if display_opt:
            pdt = pdt[0]
        obj = guard(extracted[6])
        if not display_opt:
            obj = EC.Entity(obj[0], tag=obj[1])
            obj.dt = extracted[4]
            obj.all = extracted[5]
            for attr in extracted[4]:
                setattr(obj, attr[0], None)  # leave this empty for now ...
        else:
            obj = obj[0]
        graph.add_edge(sbj, obj, object=pdt)
    return graph

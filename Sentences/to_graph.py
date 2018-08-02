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
    elif tier == 1.3 or tier == 1.4:  # basically the same
        sbj = extracted[3]
        if not display_opt:
            sbj = EC.Entity(sbj[0], tag=sbj[1])
            sbj.dt = extracted[0]
            sbj.all = extracted[1]
            sbj.adt = extracted[2]
            if tier == 1.4:
                sbj.toi = extracted[13]  # BUG: problems with index, deprecated anyway but had better fix
            for attr in extracted[1]:
                setattr(sbj, attr[0], None)  # leave this empty for now ...
        else:
            sbj = sbj[0]
        pdt = extracted[4]
        if display_opt:
            pdt = pdt[0]
        obj = guard(extracted[8])
        if obj != nil:
            if not display_opt:
                obj = EC.Entity(obj[0], tag=obj[1])
                obj.dt = extracted[9]
                obj.all = extracted[10]
                obj.adt = extracted[11]
                if tier == 1.4:
                    obj.toi = extracted[14]
                for attr in extracted[4]:
                    setattr(obj, attr[0], None)
            else:
                obj = obj[0]
        graph.add_edge(sbj, obj, object=pdt)
    elif tier == 1.5:
        sbj = extracted[3]
        if not display_opt:
            sbj = EC.Entity(sbj[0], tag=sbj[1])
            sbj.dt = extracted[0]
            sbj.all = extracted[1]
            sbj.adt = extracted[2]
            sbj.toi = extracted[11]
            sbj.tpa = extracted[4]
            for attr in extracted[1]:
                setattr(sbj, attr[0], None)
        else:
            sbj = sbj[0]
        pdt = extracted[5]
        if display_opt:
            pdt = pdt[0]
        obj = guard(extracted[9])
        if obj != nil:
            if not display_opt:
                obj = EC.Entity(obj[0], tag=obj[1])
                obj.dt = extracted[6]
                obj.all = extracted[7]
                obj.adt = extracted[8]
                obj.toi = extracted[16]
                obj.tpa = extracted[12]
                for attr in extracted[4]:
                    setattr(obj, attr[0], None)
            else:
                obj = obj[0]
        graph.add_edge(sbj, obj, object=pdt)
    elif tier == 2.1:  # with the new twist with sentence
        sbj = extracted["sbj"]
        if not display_opt:
            sbj = EC.Entity(sbj[0], tag=sbj[1])
            sbj.dt = extracted["sbj_dt"]
            sbj.all = extracted["sbj_att"]
            sbj.adt = extracted["sbj_adt"]
            sbj.toi = extracted["sbj_toi"]
            sbj.tpa = extracted["sbj_tpa"]
            for attr in extracted["sbj_att"]:
                setattr(sbj, attr[0], None)
        else:
            sbj = sbj[0]
        pdt = extracted["pdt"]
        if display_opt:
            pdt = pdt[0]
        obj = guard(extracted["obj"])
        if obj != nil:
            if not display_opt:
                obj = EC.Entity(obj[0], tag=obj[1])
                obj.dt = extracted["obj_dt"]
                obj.all = extracted["obj_att"]
                obj.adt = extracted["obj_adt"]
                obj.toi = extracted["obj_toi"]
                obj.tpa = extracted["obj_tpa"]
                for attr in extracted[4]:
                    setattr(obj, attr[0], None)
            else:
                obj = obj[0]
        graph.add_edge(sbj, obj, object=pdt)
    return graph

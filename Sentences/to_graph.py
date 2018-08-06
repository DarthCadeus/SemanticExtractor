import networkx as nx
import matplotlib.pyplot as plt
nil = lambda: None
guard = lambda x: nil if x is None else x
def to_graph(extracted, tier=None, display_opt=False):
    graph = nx.DiGraph()
    # TODO: handle PRPs separately
    if tier == 1.1:
        sbj = extracted[0]
        if not display_opt:
            sbj = EC.Entity(sbj[0], tag=sbj[1])
        else:
            if type(sbj) is tuple:
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
    elif tier == 2.1 or tier == 2.2 or tier == 2.3:  # with the new twist with sentence
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
    elif tier >= 3.1:  # with the new twist with sentence
        sbj = extracted["sbj"]
        if type(sbj) is tuple:
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
        else:
            if tier == 3.2:
                pdt = EC.Container(body=pdt, passive=extracted["pss_vce"], att=extracted["pdt_ptc"])
            else:
                pdt = EC.Container(body=pdt, passive=extracted["pss_vce"])
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
    if display_opt:
        nx.draw(graph, pos={
            sbj: (10, 10),
            obj: (100, 100)
        }, with_labels=True, node_size=600)
        plt.text(55, 55, pdt, fontsize=16, bbox=dict(facecolor="white"))
        if tier >= 2.2:
            if tier == 2.2:
                if extracted["disagree"]:
                    plt.text(0, 100, "DISAGREEMENT!", fontsize=30, bbox=dict(facecolor="red"))
            if tier >= 2.3:
                if extracted["svb_dis"]:
                    plt.text(0, 100, "Subject-Verb disagreement!", fontsize=10, bbox=dict(facecolor="red"))
                if extracted["spn_dis"]:
                    plt.text(0, 90, "Subject Pronoun case error!", fontsize=10, bbox=dict(facecolor="red"))
                if extracted["opn_dis"]:
                    plt.text(0, 80, "Object Pronoun case error!", fontsize=10, bbox=dict(facecolor="red"))
        if tier >= 3.1:
            if extracted["pss_vce"]:
                plt.text(0, 70, "Passive Voice", fontsize=10, bbox=dict(facecolor="yellow"))
            if tier >= 3.2:
                for char in range(len(extracted["pdt_ptc"])):
                    chartext = extracted["pdt_ptc"][char]
                    plt.annotate(chartext[0], (55, 55), (65+5*(char+1), 55), arrowprops={
                        "arrowstyle": "->"
                    })
        sbj_stf = extracted["sbj_att"]  # subject stuff
        for char in range(len(sbj_stf)):
            chartext = sbj_stf[char]
            plt.annotate(chartext[1][0], (10, 10), (10, 10+5*(char+1)), arrowprops={
                "arrowstyle": "->"
            })
        obj_stf = extracted["obj_att"]
        for char in range(len(obj_stf)):
            chartext = obj_stf[char]
            plt.annotate(chartext[1][0], (100, 100), (100, 100-5*(char+1)), arrowprops={
                "arrowstyle": "->"
            })
    return graph

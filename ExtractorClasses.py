"""
Newest version of all Classes used in Semantic Extraction here
Fixed several bugs: (v0.2)
    1. Pointer class failed to deal with "&any" cases not having an POS tag
    2. Action class failing to pass index to Pointer (it can't)
    3. Pointer class did not deal with "it"
Modifications:
    1. made all index arguments optional
    2. Added default tagging for Entity and Action
    3. Added plural argument to Pointer class for "you" cases
    4. simplified the code

ALL USAGES OF THE CLASSES SHOULD REFER TO THE NEWEST VERSION HERE (CURRENTLY
V0.2, INSTEAD OF IN sme.py

Fixed several bugs: (v0.3)
    1. __str__ method would not return the debug-friendly version
    2. partition method in utils can only work with one partition at a time
    3. partition method in utils excludes last item
    4. docstring contains misspelled words
Modifications:
    1. added __str__ method to Relation
    2. allowed Relations to construct based on the partitioned result
    3. added index support for Relation

ALL USAGES OF THE CLASSES SHOULD REFER TO THE NEWEST VERSION HERE (CURRENTLY
V0.3, INSTEAD OF IN sme.py

sme.py IS NOW DEPRECATED, SO IS v0.2
"""
import utils


class Entity:
    def __init__(self, name, index=None, tag=None):
        # the name of the Entity, which is the text it was created from
        self.name = name
        # the index of that text
        self.index = index
        # the POS tag that came with it
        self.tag = tag if tag else "NN"  # noun by default
        # the attributes or characteristics that it has
        self.attributes = []

    def __str__(self):
        # for easier debugging
        return "Entity <name:" \
               + self.name + "> with attributes " \
                             "[["+utils.ls(self.attributes)+"]]" \
               + " with index at "+str(self.index)


class Action(Entity):
    def __init__(self, name, index, tag=None, target=None):
        # init the super class
        Entity.__init__(self, name, index, tag)
        self.target = target if target else Pointer("&any")
        self.tag = self.tag if self.tag else "v"

    def __str__(self):
        return str("Action <name:"
                   + self.name + "> with attributes"
                   + " [["+utils.ls(self.attributes)+"]] and target: <"
                   + utils.ls(self.target)
                   + "> with index at " + str(self.index))


class Pointer:
    def __init__(self, target, plural=None, index=None):
        self.index = index
        self.tag = "PRP" if target != "&any" else None
        target = target.lower()
        if target[0] == "&":  # already in pointer form
            self.target = (target.strip("&"), None)
        else:
            if target in ["I", "me"]:
                self.target = ("self", None)  # standard form
            # this way the program would not need to check
            # length before accessing the target
            elif target in ["we", "us"]:
                self.target = ("self", "pl")
            elif target in ["this"]:
                self.target = ("self", "ob")
            elif target in ["these"]:
                self.target = ("self", "pb")
            elif target == "you":
                if plural is None:
                    self.target = ("opp", "du")  # two possibilities
                elif plural is True:
                    self.target = ("opp", "pl")
                else:
                    self.target = ("opp", None)
            elif target in ["it"]:
                self.target = ("trd", None)
            elif target in ["he", "him"]:
                self.target = ("trd", "ml")
            elif target in ["she", "her"]:
                self.target = ("trd", "fl")
            elif target in ["they", "them"]:
                self.target = ("trd", "pl")
            elif target in ["that"]:
                self.target = ("trd", "ob")
            elif target in ["those"]:
                self.target = ("trd", "pb")
            elif target == "all":
                self.target = ("all", None)
            else:
                self.target = ("uid", None)  # not identified

    def __str__(self):
        return "Pointer <" + "&" + self.target[0] + \
               "(" + (self.target[1] if self.target[1] else "sd") + ")>"


class Characteristic:
    def __init__(self, name, index=None, tag=None):
        self.name = name
        self.index = index
        self.tag = tag

    def __str__(self):
        return "<Characteristic Object with name:"+self.name+">"


class Relation:
    def __init__(self, constructor, index=None):
        # name, indexrange = None, tag = None
        self.name = " ".join(list(map(lambda x: x[0], constructor)))
        # self.indexrange = indexrange if indexrange else []
        self.index = index
        self.tag = list(map(lambda x: x[1], constructor))

    def __str__(self):
        return f"<Relationship object with name: {self.name} at index {self.index}>"


class Node:
    def __init__(self, entity):
        self.entity = entity
        self.neighbors = {}

    def addNeighbor(self, entity, relationship):
        self.neighbors[entity] = relationship

    def removeNeighbor(self, entity):
        return self.neighbors.pop(entity, None)

    @staticmethod
    def build(entity):
        return Node(entity)

    def spstring(self):
        dcs = "\n"
        for i in self.neighbors:
            dcs += "("+str(i.entity)+": "+str(self.neighbors[i])+"), "
        return dcs

    def getNeighbors(self, caller=None, form="dict"):
        if type(caller) != list:
            caller = [caller]
        if form == "dict":
            ret = {}
            for neighbor in self.neighbors:
                if neighbor not in caller:
                    ret[neighbor] = self.neighbors[neighbor]
        elif form == "list":
            ret = []
            for neighbor in self.neighbors:
                if neighbor not in caller:
                    ret.append((neighbor, self.neighbors[neighbor]))
        else:
            ret = []
        return ret

    def __str__(self):
        return f"<Node object with entity {str(self.entity)} >"


class CorpusGraph:
    def __init__(self, entities):
        self.nodes = list(map(Node.build, entities))

    def getNodeByName(self, name):
        for e in self.nodes:
            if type(e.entity) != Pointer:
                if e.entity.name == name:
                    return e
        return False

    def getNodeByEntity(self, ent):
        for e in self.nodes:
            if e.entity == ent:
                return e
        return False

    def getNodeByIndex(self, idx):
        for n in self.nodes:
            if n.entity.index == idx:
                return n
        return False

    def getNodeById(self, index):
        return self.nodes[index]

    def addEntity(self, entity):
        self.nodes.append(Node(entity))

    def linkEntities(self, n1, n2, relationship):  # nodes
        if n1 not in self.nodes:
            self.nodes.append(n1)
        if n2 not in self.nodes:
            self.nodes.append(n2)
        n1.addNeighbor(n2, relationship)
        n2.addNeighbor(n1, relationship)

    def iterate(self):
        visited = []
        ret = [self.nodes[0]]
        for n in self.nodes:
            nbs = n.getNeighbors(caller=visited, form="list")
            if nbs:
                ret.append(list(reversed(nbs[0])))
                visited.append(n)
            else:
                break
        return utils.flatten(ret)

    def to_networkx(self, display_opt=False):
        try:
            import networkx
            graph = networkx.Graph()

            def verify(x):
                if type(x) == Node:
                    return len(x.neighbors) > 0
                else:
                    return True

            it = list(filter(lambda x: verify(x), self.iterate()))
            for i in range(0, len(it) - 2, 2):
                if display_opt:
                    graph.add_edge(it[i].entity.name, it[i + 2].entity.name, object=it[i + 1].name)
                else:
                    graph.add_edge(it[i], it[i + 2], object=it[i + 1])
            return graph
        except ImportError:
            return False

    def draw(self, graph, options, force_pillow=False, force_ascii=False):
        if force_ascii:
            return self._ascii_draw()
        if force_pillow:
            return self._pillow_draw()
        try:
            import networkx
            networkx.draw(graph, **options)
            return "nx"
        except ImportError:
            p = self._pillow_draw()
            if p:
                return "pillow", p
            else:
                return "ascii", self._ascii_draw()

    def _pillow_draw(self):
        try:
            from PIL import Image, ImageDraw
            s = self.iterate()
            new = Image.new('RGB', (len(s) * 150, 500))
            draw = ImageDraw.Draw(new)
            cur_x = 0
            mx = 0
            for i in range(len(s)):
                if type(s[i]) == Relation:
                    fill = (102, 153, 204)
                else:
                    fill = (72, 105, 127)
                draw.rectangle([cur_x + 150 * i, 0, cur_x + 150 * (i + 1), 500], fill=fill)
                # format text
                si = str(s[i])
                ts = draw.textsize(si)[0]
                dv = ts/len(si)
                print(ts)
                if ts > 140:
                    for j in range(0, len(si), int(140/dv)):
                        si = utils.s_insert(si, "\n", j)
                draw.text((cur_x + 150 * i + 10, 10), si)
                ts = draw.multiline_textsize(si)[1]
                mx = mx if ts < mx else ts
            return new.crop([0, 0, len(s) * 150, mx+30])
        except ImportError:
            return False

    def _ascii_draw(self):
        s = self.iterate()
        sp = []
        ret = ""
        ml = 0
        for i in range(len(s)):
            si = s[i]
            if type(si) is Node:
                if type(si.entity) in [Entity, Action]:
                    if len(si.entity.name) > ml:
                        ml = len(si.entity.name)
                    sp.append((si.entity.name, ""))
                elif type(si.entity) == Pointer:
                    if len(si.entity.target[0]) > ml:
                        ml = len(si.entity.target[0])
                    sp.append((si.entity.target[0], ""))
            else:
                if len(si.name) > ml:
                    ml = len(si.name)
                sp.append((si.name, "rel"))

        ml += 4  # leave a padding

        for i in range(len(sp)):
            if sp[i][1] == "rel":
                si = sp[i][0].center(ml)
                ret += ("||".center(ml) + "\n") * 2
                ret += si + "\n"
                ret += ("||".center(ml) + "\n") * 2
                ret += "\\/".center(ml) + "\n"
            else:
                si = sp[i][0].center(ml, "#")
                ret += ("#"*ml + "\n")*2
                ret += si + "\n"
                ret += ("#" * ml + "\n") * 2
        return ret


if __name__ == "__main__":
    e1 = Entity("John")
    e2 = Entity("Jake")
    e3 = Entity("Mary")
    e4 = Entity("Ben")
    r1 = Relation([("likes", "VB")])
    r2 = Relation([("dislikes", "VB")])
    r3 = Relation([("meets", "VB")])
    g1 = CorpusGraph([e1, e2, e3, e4])
    n1 = g1.getNodeByEntity(e1)
    n2 = g1.getNodeByEntity(e2)
    n3 = g1.getNodeByEntity(e3)
    n4 = g1.getNodeByEntity(e4)
    g1.linkEntities(n1, n2, r1)
    g1.linkEntities(n2, n3, r2)
    g1.linkEntities(n3, n4, r3)
    gx = g1.to_networkx(True)
    image = g1.draw(gx, {
        "node_size": 700,
        "with_labels": True
    }, force_ascii=True)
    print(image)
    # plt.savefig("test.png")

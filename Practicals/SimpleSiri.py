"""
This is a demonstration of the capabilities of the current processor.
Using d.0.1 processing combined with processor 2.2.1, this file will
make a simple siri-like app with textual input and a simulated file system
"""
import sys
sys.path.append("../Sentences")
sys.path.append("..")
import ExtractLib as EL
import ExtractorClasses as EC
import utils
import networkx as nx
import inspect

filesystem = {
    "hello.txt": {
        "date created": -1,  # -1 for yesterday ...
        "author": "user",
        "content": "Hello"
    },
    "world.txt": {
        "date created": 0,
        "author": "another_user",
        "content": "World"
    },
    "punctuation.folder": {
        "date created": -3,
        "author": "user",
        "filesystem": {
            "comma.md": {
                "date created": -4,
                "author": "another_user",
                "content": ","
            },
            "exclaim.md": {
                "date created": -1,
                "author": "user",
                "content": "!"
            }
        }
    }
}

def filter_filesystem(filesystem, criteria, path="/"):
    for file in filesystem:
        type = file.split(".")[::-1][0]
        if type != "folder":
            date = filesystem[file]["date created"]
            author = filesystem[file]["author"]
            content = filesystem[file]["content"]
            if criteria(type, date, author, content):
                yield filesystem[file]
        else:
            return filter_filesystem(filesystem[file]["filesystem"], criteria)


def filesystem_by_date(filesystem):
    ks = list(filesystem.keys())
    nd = dict([(x, filesystem[x]["date created"]) for x in ks])
    return sorted(list(nd.keys()), key=nd.get)

# start app engine
while True:
    statement = input("Say something... ")
    if statement == "quit":
        break
    elif statement == "":
        continue
    sem = EL.extract(statement, graph=False)
    obj = sem.obj
    obj_bdy = sem["obj"]
    pdt = sem.pdt
    pdt_bdy = sem["pdt"]
    typ = "any"
    # print(sem)
    if pdt_bdy[0].lower() == "open":
        if obj["adt"]:
            owner = obj["adt"][0][0]  # has to be the first
        else:
            owner = "any"
        # no, I am serious
        mds = None
        num = None
        qualifications = list(map(lambda x: x[1], obj["att"]))
        for q in qualifications:
            if q[0] in ["recent", "old"]:
                mds = q
            elif q[1] == "CD":
                num = utils.machinize(q[0])
        if obj_bdy[0].lower() != "file":
            typ = obj_bdy[0].lower()

        def evaluate(t, d, a, c):
            ret = True
            if mds[0] == "recent":
                if d < -2:
                    ret = False
            else:
                if d > -2:
                    ret = False
            return ret

        fsd = filesystem_by_date(filesystem)
        if mds[0] == "recent" and num:
            print(fsd[:num])
        elif mds[0] == "old" and num:
            print(fsd[::-1][num])
        elif not num:
            print(list(filter_filesystem(filesystem, evaluate)))

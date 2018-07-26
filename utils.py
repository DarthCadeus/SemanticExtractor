# for operations
def dict_max(d):
    """ a) create a list of the dict's keys and values;
         b) return the key with the max value"""
    v = list(d.values())
    k = list(d.keys())
    return k[v.index(max(v))]


def findall(item, l):
    for i in range(0, len(l)):
        if l[i] == item:
            yield i


def getall(indices, l):
    for i in indices:
        yield l[i]


def fuzzy_count(l, num, err=3):
    # l must be an array of numbers
    count = 0
    for i in l:
        if num-err < i < num+err:
            count += 1
    return count


def in_list(l, *args):
    for arg in args:
        if arg not in l:
            yield False
        else:
            yield True


def alternative_splits(l, *args):
    if type(args[0]) is list and len(args) == 1:
        args = args[0]
    for i in args:
        yield l.split(i)


def partition(l, part):
    pt = []
    its = 0
    for p1 in range(len(l)):
        p = l[p1]
        if p == part:
            if pt:
                pt.append((its, ))
                yield pt
                pt = []
                its = p1+1
            else:
                its = p1+1
        else:
            pt.append(p)
    if pt:
        pt.append((its, ))
        yield pt


def printl(l, prefix=""):
    for x in l:
        if type(x) == list or type(x) == tuple:
            printl(x, prefix=prefix+"   ")
        else:
            print(prefix + str(x))


def ls(l):
    ret = ""
    for x in l:
        if type(x) == list:
            ret += "[" + ls(x) + "]"
        else:
            ret += str(x)
        ret += ", "
    return ret


def getEntityByIndex(idx, entities):
    for i in entities:
        if i.index == idx:
            return i


def flatten(l):
    ret = []
    for i in l:
        if type(i) == list:
            ret.extend(flatten(i))
        else:
            ret.append(i)
    return ret


def correspond(idxr, idxl):
    for i in idxl:
        if idxr[0] < i < idxr[1]:
            yield i


def getRelationByIndex(rels, idx):
    for rel in rels:
        if rel.index == idx:
            return rel
    return False


def s_insert(string, char, index):
    return string[:index] + char + string[index:]


if __name__ == "__main__":
    print(list(partition([1, None, None, 4, 2, None, 1], None)))

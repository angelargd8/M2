from graphviz import Digraph
import itertools

#esta funcion la mejoro y dio chat, porque la otra daba error jiji
def render_ast(root, out="./output/ast.png"):
    from dataclasses import is_dataclass, fields
    dot = Digraph(graph_attr={"rankdir":"TB"})
    counter = [0]
    def id(): counter[0]+=1; return f"n{counter[0]}"
    def walk(node):
        nid = id()
        label = type(node).__name__
        dot.node(nid, label)
        if is_dataclass(node):
            for f in fields(node):
                val = getattr(node, f.name)
                if val is None: continue
                cid = id(); dot.node(cid, f.name)
                dot.edge(nid, cid)
                if isinstance(val, list):
                    for item in val:
                        kid = walk(item)
                        dot.edge(cid, kid)
                else:
                    kid = walk(val)
                    dot.edge(cid, kid)
        else:
            vid = id(); dot.node(vid, str(node))
            dot.edge(nid, vid)
        return nid
    walk(root)
    dot.render(out, format="png", cleanup=True)
    return out
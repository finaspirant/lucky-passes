"""AST mutation operators.

find_sites lists every concrete mutation in a module, in a deterministic order.
Each site has a key; mutate(source, keys) re-applies exactly those mutations, so a
task is reproducible from its solution source and recorded keys.
"""

import ast
from dataclasses import dataclass, field
from typing import Callable

TYPES = ["off_by_one", "flipped_comparison", "wrong_initial_value", "inverted_condition", "swapped_arguments"]
FLIPS = {ast.Lt: ast.LtE, ast.LtE: ast.Lt, ast.Gt: ast.GtE, ast.GtE: ast.Gt, ast.Eq: ast.NotEq, ast.NotEq: ast.Eq}
OP_TEXT = {ast.Lt: "<", ast.LtE: "<=", ast.Gt: ">", ast.GtE: ">=", ast.Eq: "==", ast.NotEq: "!="}


@dataclass
class Site:
    kind: str
    function: str
    line: int
    col: int
    detail: str
    apply: Callable[[], None] = field(repr=False)

    @property
    def key(self):
        return f"{self.kind}:{self.line}:{self.col}:{self.detail}"

    @property
    def is_helper(self):
        name = self.function.split(".")[-1]
        return name.startswith("_") and not name.startswith("__")


def normalize(source):
    return ast.unparse(ast.parse(source)) + "\n"


def mutate(source, keys):
    tree = ast.parse(source)
    sites = {site.key: site for site in find_sites(tree)}
    for key in keys:
        sites[key].apply()
    return ast.unparse(tree) + "\n"


def find_sites(tree):
    """List mutation sites. Folds negative int literals in tree in place (unparses identically)."""
    _fold_negative_constants(tree)
    local_names = _local_callables(tree)
    sites = []
    for function, func in _functions(tree):
        skip = set()
        for node in ast.walk(func):
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and _wrong_value(node.value) is not None:
                skip.add(id(node.value))
            if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant):
                skip.add(id(node.slice))
        for node in ast.walk(func):
            sites += _sites_for(node, function, skip, local_names)
    return sites


class _FoldNegatives(ast.NodeTransformer):
    def visit_UnaryOp(self, node):
        self.generic_visit(node)
        operand = node.operand
        if isinstance(node.op, ast.USub) and isinstance(operand, ast.Constant) and type(operand.value) is int:
            return ast.copy_location(ast.Constant(-operand.value), node)
        return node


def _fold_negative_constants(tree):
    """Treat -1 as one constant, so off_by_one gives 0 or -2 rather than -0 or -2."""
    _FoldNegatives().visit(tree)


def _functions(tree):
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            yield node.name, node
        elif isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    yield f"{node.name}.{item.name}", item


def _local_callables(tree):
    return {name.split(".")[-1] for name, _ in _functions(tree)}


def _sites_for(node, function, skip, local_names):
    """Sites at node. skip holds ids of constants that are initial values or subscript indexes:
    initial values belong to wrong_initial_value, and a shifted constant index tends to
    raise an immediate IndexError."""
    def site(kind, at, detail, apply):
        return Site(kind, function, at.lineno, at.col_offset, detail, apply)

    found = []
    if isinstance(node, ast.Constant) and type(node.value) is int and id(node) not in skip:
        for delta in (1, -1):
            new = node.value + delta
            found.append(site("off_by_one", node, f"{node.value}->{new}", lambda n=node, v=new: setattr(n, "value", v)))
    if isinstance(node, ast.Compare):
        for k, op in enumerate(node.ops):
            if type(op) in FLIPS:
                new_op = FLIPS[type(op)]
                detail = f"op{k}:{OP_TEXT[type(op)]}->{OP_TEXT[new_op]}"
                found.append(site("flipped_comparison", node, detail,
                                  lambda n=node, k=k, o=new_op: n.ops.__setitem__(k, o())))
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and _wrong_value(node.value) is not None:
        new_value = _wrong_value(node.value)
        detail = f"{ast.unparse(node.value)}->{ast.unparse(new_value)}"
        found.append(site("wrong_initial_value", node, detail, lambda n=node, v=new_value: setattr(n, "value", v)))
    if isinstance(node, (ast.If, ast.While, ast.IfExp)):
        found.append(site("inverted_condition", node, "test", lambda n=node: setattr(n, "test", _invert(n.test))))
    if isinstance(node, ast.comprehension):
        for k, cond in enumerate(node.ifs):
            found.append(site("inverted_condition", cond, f"if{k}",
                              lambda n=node, k=k: n.ifs.__setitem__(k, _invert(n.ifs[k]))))
    if isinstance(node, ast.Call) and _callee(node) in local_names:
        args = node.args
        for k in range(len(args) - 1):
            plain = not any(isinstance(a, ast.Starred) for a in args[k:k + 2])
            if plain and ast.dump(args[k]) != ast.dump(args[k + 1]):
                found.append(site("swapped_arguments", node, f"args{k},{k + 1}", lambda a=args, k=k: _swap(a, k)))
    return found


def _wrong_value(value):
    """The wrong value to substitute for an int, bool or str literal, or None for anything else."""
    if not isinstance(value, ast.Constant):
        return None
    v = value.value
    if type(v) is bool:
        return ast.Constant(not v)
    if type(v) is int:
        return ast.Constant({0: 1, 1: 0}.get(v, 0))
    if isinstance(v, str):
        return ast.Constant(" " if v == "" else "")
    return None


def _invert(test):
    if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
        return test.operand
    return ast.UnaryOp(ast.Not(), test)


def _callee(call):
    if isinstance(call.func, ast.Name):
        return call.func.id
    if isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Name) and call.func.value.id == "self":
        return call.func.attr
    return None


def _swap(args, k):
    args[k], args[k + 1] = args[k + 1], args[k]

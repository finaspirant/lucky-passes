import ast

from tasks.gen.mutate import Site, find_sites, mutate, normalize

SOURCE = normalize('''
def total(items):
    """Sum items below the limit."""
    result = 0
    for item in items:
        if item < 10:
            result += _weigh(item, 2)
    return result


def _weigh(value, factor):
    return value * factor
''')


def sites_of(kind):
    return [s for s in find_sites(ast.parse(SOURCE)) if s.kind == kind]


def test_each_operator_changes_the_source():
    for kind in ["off_by_one", "flipped_comparison", "wrong_initial_value", "inverted_condition", "swapped_arguments"]:
        sites = sites_of(kind)
        assert sites, kind
        assert mutate(SOURCE, [sites[0].key]) != SOURCE


def test_specific_mutations():
    flip = sites_of("flipped_comparison")[0]
    assert "item <= 10" in mutate(SOURCE, [flip.key])
    init = sites_of("wrong_initial_value")[0]
    assert "result = 1" in mutate(SOURCE, [init.key])
    invert = sites_of("inverted_condition")[0]
    assert "if not item < 10" in mutate(SOURCE, [invert.key])
    swap = sites_of("swapped_arguments")[0]
    assert "_weigh(2, item)" in mutate(SOURCE, [swap.key])


def test_initial_values_are_not_also_off_by_one_sites():
    details = {s.detail for s in sites_of("off_by_one")}
    assert "0->1" not in details and "0->-1" not in details


def test_keys_are_unique_and_reproducible():
    keys = [s.key for s in find_sites(ast.parse(SOURCE))]
    assert len(keys) == len(set(keys))
    assert keys == [s.key for s in find_sites(ast.parse(SOURCE))]
    two = [sites_of("flipped_comparison")[0].key, sites_of("swapped_arguments")[0].key]
    assert mutate(SOURCE, two) == mutate(SOURCE, two)


def test_docstring_is_kept():
    key = sites_of("off_by_one")[0].key
    assert ast.get_docstring(ast.parse(mutate(SOURCE, [key])).body[0]) == "Sum items below the limit."


def test_helper_flag():
    def helper(function):
        return Site("off_by_one", function, 1, 0, "", lambda: None).is_helper

    assert helper("_weigh") and helper("RingBuffer._slot")
    assert not helper("total") and not helper("RingBuffer.__init__") and not helper("RingBuffer.push")


def test_negative_constant_is_one_unit():
    source = normalize("def f(xs):\n    best = xs[0]\n    return best - -1\n")
    sites = {s.detail: s.key for s in find_sites(ast.parse(source)) if s.kind == "off_by_one"}
    assert set(sites) == {"-1->0", "-1->-2"}
    assert "best - 0" in mutate(source, [sites["-1->0"]])
    assert "best - -2" in mutate(source, [sites["-1->-2"]])


def test_subscript_indexes_are_not_sites():
    source = normalize("def f(pairs):\n    return pairs[-1][1] + 5\n")
    details = {s.detail for s in find_sites(ast.parse(source)) if s.kind == "off_by_one"}
    assert details == {"5->6", "5->4"}


def test_wrong_initial_value_skips_lists_and_none():
    source = normalize("def f():\n    a = []\n    b = None\n    c = True\n    d = ''\n    return a, b, c, d\n")
    details = sorted(s.detail for s in find_sites(ast.parse(source)) if s.kind == "wrong_initial_value")
    assert details == ["''->' '", "True->False"]

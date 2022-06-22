import itertools

import graphviz
import pulp


class SymmetricDict(dict):
    @classmethod
    def sort_tuple(cls, key):
        return tuple(sorted(key))

    def __getitem__(self, key):
        key = self.__class__.sort_tuple(key)
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        key = self.__class__.sort_tuple(key)
        return super().__setitem__(key, value)


def plain_plot(weight):
    g = graphviz.Graph(
        "plain",
        format="png",
        node_attr={"fontname": "Roboto Mono", "shape": "box"},
        edge_attr={"fontname": "Roboto Mono"},
    )
    for (i, j) in weight:
        g.edge(i, j, label=str(weight[(i, j)]))
    g.view()


def solve(names, weight, n):
    ilp = pulp.LpProblem("friends", pulp.LpMaximize)
    vertex_variable = {}
    for name in names:
        vertex_variable[name] = pulp.LpVariable(name=name, cat=pulp.const.LpBinary)

    edge_variable = SymmetricDict()
    for (i, j) in itertools.combinations(names, 2):
        edge_variable[(i, j)] = pulp.LpVariable(
            name=f"{i}-{j}", cat=pulp.const.LpBinary
        )
        ilp += edge_variable[(i, j)] <= vertex_variable[i]
        ilp += edge_variable[(i, j)] <= vertex_variable[j]
        ilp += edge_variable[(i, j)] >= vertex_variable[i] + vertex_variable[j] - 1

    ilp += sum(vertex_variable[i] for i in names) == n
    ilp += sum(
        edge_variable[(i, j)] * weight[(i, j)]
        for i, j in itertools.combinations(names, 2)
    )

    ilp.solve()

    print("All variables:")
    for v in ilp.variables():
        print(v.name, "=", v.varValue)

    g = graphviz.Graph(
        f"graph_n={n}",
        format="png",
        graph_attr={"fontname": "Roboto Mono", "label": f"n={n}"},
        node_attr={"fontname": "Roboto Mono", "shape": "box"},
        edge_attr={"fontname": "Roboto Mono"},
    )
    for name in vertex_variable:
        color = "#c1e4a5" if pulp.value(vertex_variable[name]) == 1 else "grey"
        g.node(name, style="filled", fillcolor=color)

    for (i, j) in weight:
        color = "#c1e4a5" if pulp.value(edge_variable[(i, j)]) == 1 else "grey"
        g.edge(i, j, label=str(weight[(i, j)]), color=color)
    g.view()


def main():
    names = ["Tony", "Vito", "Paulie", "Silvio", "Furio"]

    weight = SymmetricDict()
    weight[("Tony", "Vito")] = 1
    weight[("Tony", "Paulie")] = 2
    weight[("Tony", "Silvio")] = 3
    weight[("Tony", "Furio")] = 1

    weight[("Vito", "Paulie")] = -1
    weight[("Vito", "Silvio")] = 1
    weight[("Vito", "Furio")] = 0

    weight[("Paulie", "Silvio")] = 2
    weight[("Paulie", "Furio")] = 2

    weight[("Silvio", "Furio")] = 2

    plain_plot(weight)
    solve(names, weight, 3)

    names_c = ["Tony", "Vito", "Paulie", "Silvio"]

    weight_c = SymmetricDict()
    weight_c[("Tony", "Vito")] = 100
    weight_c[("Tony", "Paulie")] = -101
    weight_c[("Tony", "Silvio")] = -101

    weight_c[("Vito", "Paulie")] = 1
    weight_c[("Vito", "Silvio")] = 1

    weight_c[("Paulie", "Silvio")] = 1

    plain_plot(weight_c)
    print("n=2")
    solve(names_c, weight_c, 2)
    print("----")
    print("n=3")
    solve(names_c, weight_c, 3)


if __name__ == "__main__":
    main()

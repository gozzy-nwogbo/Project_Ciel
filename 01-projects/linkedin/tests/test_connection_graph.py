from atom_loader import AtomLoader
from connection_graph import ConnectionGraph


def test_edges_for_atom(atom_source):
    loader = AtomLoader(atom_source)
    graph = ConnectionGraph(loader.load_all())
    edges = graph.edges_for("sample-concept")
    assert len(edges) >= 1
    mech = next(e for e in edges if e.connection_type == "mechanism")
    assert mech.from_title == "Sample Concept"
    assert mech.to_title == "Another Concept"


def test_edges_by_type(atom_source):
    loader = AtomLoader(atom_source)
    graph = ConnectionGraph(loader.load_all())
    mech_edges = graph.edges_by_type("mechanism")
    assert len(mech_edges) == 1

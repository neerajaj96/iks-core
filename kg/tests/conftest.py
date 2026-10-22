from types import SimpleNamespace

import pytest

from iks_kg.build import build, validate


@pytest.fixture(scope="session")
def built():
    graph, stats, coverage, audit = build()
    conforms, results_text = validate(graph)
    return SimpleNamespace(
        graph=graph,
        stats=stats,
        coverage=coverage,
        audit=audit,
        conforms=conforms,
        results_text=results_text,
    )

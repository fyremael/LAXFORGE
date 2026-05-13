from laxforge.examples.mkdv_second_jet import validate


def test_second_jet_mkdv_zero_curvature():
    result = validate()
    assert all(result["checks"].values())

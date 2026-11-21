from src.parser import parse_formula
from src.verifier import check_equivalence

def test_equivalent_syntax_variants():
    assert check_equivalence(parse_formula("M -> D", {"M","D"}), parse_formula("NOT M OR D", {"M","D"}))["equivalent"] is True
def test_reverse_implication_is_not_equivalent():
    r=check_equivalence(parse_formula("M -> D", {"M","D"}), parse_formula("D -> M", {"M","D"}))
    # Either asymmetric assignment distinguishes the two directions.
    assert r["status"] == "SAT" and r["generated_value"] != r["reference_value"]

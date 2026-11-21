from src.logic import evaluate
from src.parser import parse_formula
from src.truth_table import make_truth_table

def test_implication_truth_values():
    f=parse_formula("M -> D", {"M","D"}); assert [r["result"] for r in make_truth_table(f)] == [True,True,False,True]
def test_truth_table_size(): assert len(make_truth_table(parse_formula("A AND B AND C", {"A","B","C"}))) == 8

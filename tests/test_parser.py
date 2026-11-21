import pytest
from src.parser import FormulaError, parse_formula, tokenize
from src.logic import evaluate

def test_tokenization_and_symbols(): assert tokenize("¬M ∧ (D → A)") == ["NOT","M","AND","(","D","IMPLIES","A",")"]
def test_precedence():
    f = parse_formula("A OR B AND C", {"A","B","C"})
    assert evaluate(f, {"A":False,"B":True,"C":False}) is False
def test_unknown_rejected():
    with pytest.raises(FormulaError): parse_formula("M AND X", {"M"})
def test_invalid_rejected():
    with pytest.raises(FormulaError): parse_formula("M AND", {"M"})

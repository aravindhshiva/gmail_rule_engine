import pytest
from rule_engine.rule import Rule


def test_contains():
    rule = Rule(field="subject", predicate="contains", value="urgent")
    assert rule.build_query() == "SUBJECT LIKE '%urgent%'"


def test_does_not_contain():
    rule = Rule(field="body", predicate="does_not_contain", value="spam")
    assert rule.build_query() == "BODY NOT LIKE '%spam%'"


def test_equals():
    rule = Rule(field="subject", predicate="equals", value="Meeting")
    assert rule.build_query() == "SUBJECT = 'Meeting'"


def test_does_not_equal():
    rule = Rule(field="subject", predicate="does_not_equal", value="Newsletter")
    assert rule.build_query() == "SUBJECT != 'Newsletter'"


def test_less_than_months():
    rule = Rule(field="received_date", predicate="less_than_months", value=3)
    assert rule.build_query() == "RECEIVEDDATE > datetime('now', '-3 months')"


def test_greater_than_days():
    rule = Rule(field="received_date", predicate="greater_than_days", value=7)
    assert rule.build_query() == "RECEIVEDDATE < datetime('now', '-7 days')"


def test_invalid_predicate():
    rule = Rule(field="subject", predicate="not_supported", value="value")
    with pytest.raises(NotImplementedError) as excinfo:
        rule.build_query()
    assert "Predicate not_supported is not implemented." in str(excinfo.value)

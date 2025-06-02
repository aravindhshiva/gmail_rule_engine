import json

from rule_engine.engine import Engine

sample_rules_json = {
    "conditionType": "ALL",
    "rules": [
        {"field": "subject", "predicate": "equals", "value": "Random Fake Email"}
    ],
    "actions": [
        {"type": "move_message", "destination": "INBOX"}
    ]
}
sample_rules_str = json.dumps(sample_rules_json)

def test_engine_process(mocker):
    mocker.patch("builtins.open", mocker.mock_open(read_data=sample_rules_str))

    mock_rule_instance = mocker.MagicMock()
    mock_rule_instance.build_query.return_value = "subject = 'Random Fake Email'"
    mocker.patch("rule_engine.engine.Rule", return_value=mock_rule_instance)

    mock_email_dao_instance = mocker.MagicMock()
    mock_email_dao_instance.query_email.return_value = ["email1", "email2"]
    mocker.patch("rule_engine.engine.EmailDAO", return_value=mock_email_dao_instance)

    mock_action_handler_instance = mocker.MagicMock()
    mocker.patch("rule_engine.engine.ActionHandler", return_value=mock_action_handler_instance)

    mock_validate = mocker.patch("rule_engine.engine.validate")

    engine = Engine("fake_rule_spec.json")
    engine.process()

    mock_validate.assert_called_once_with("fake_rule_spec.json")
    mock_rule_instance.build_query.assert_called_once()
    mock_email_dao_instance.query_email.assert_called_once_with("subject = 'Random Fake Email'")
    mock_action_handler_instance.process.assert_called_once()
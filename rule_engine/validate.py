import json

from jsonschema.validators import Draft202012Validator
from jsonschema.validators import exceptions

from logutils.utils import get_logger

log = get_logger()

def validate(rules_json_path):
    with open("rule_engine/spec/rules.json", "r") as rf:
        schema = json.load(rf)

    with open(rules_json_path, "r") as f:
        rules = json.load(f)

    try:
        validator = Draft202012Validator(schema)
        validator.validate(rules)
    except exceptions.ValidationError as e:
        log.failure("JSON validation error:", e.message)
        raise e

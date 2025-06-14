"""
engine.py - Rule processing engine for the Gmail Rule Engine CLI.
"""
import json
import sys
from typing import List

from jsonschema import exceptions

from db.email_dao import EmailDAO
from logutils.utils import get_logger
from model.action import Action
from model.email import Email
from rule_engine.action_handler import ActionHandler
from rule_engine.rule import Rule
from rule_engine.validate import validate

log = get_logger()


class Engine:
    """
    Engine for processing the rules and performing actions on queried emails. Does three things:

    1) Processes and builds WHERE clauses based on the rules
    2) Queries based on the built SQL command
    3) Invokes actions on the queried emails.
    """

    def __init__(self, rules_json_path: str = None):
        self.rules_json_path = rules_json_path
        with open(self.rules_json_path, "r") as f:
            self.rules_json = json.load(f)
        self.email_dao = EmailDAO()

    def get_rules(self):
        return [Rule(rule["field"], rule["predicate"], rule["value"]) for rule in self.rules_json["rules"]]

    def _get_actions(self):
        return [Action(action["type"], action.get("destination")) for action in self.rules_json["actions"]]

    def _condition_type(self):
        return self.rules_json["conditionType"]

    def _retrieve_emails(self, where_clause):
        return self.email_dao.query_email(where_clause)

    def process(self):
        try:
            validate(self.rules_json_path)
            rules = self.get_rules()

            # Process Rules (and build WHERE clause)
            rule_queries = [rule.build_query() for rule in rules]

            match self._condition_type().upper():
                case "ALL":
                    where_clause = " AND ".join(rule_queries)
                case "ANY":
                    where_clause = " OR ".join(rule_queries)
                case _:
                    raise TypeError("Invalid condition type.")

            # Retrieve Emails
            emails: List[Email] = self._retrieve_emails(where_clause)

            if not emails:
                log.failure("No emails found matching the given rules.")
                sys.exit(0)

            # Invoke action
            actions = self._get_actions()
            action_handler = ActionHandler(emails, actions)
            action_handler.process()

        except exceptions.ValidationError as e:
            log.failure("Invalid rules in rules.json, cannot proceed.")
            raise e

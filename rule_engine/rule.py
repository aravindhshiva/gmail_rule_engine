COLUMN_MAP = {
    "from_email": "FROMEMAIL",
    "to_email": "TOEMAIL",
    "subject": "SUBJECT",
    "received_date": "RECEIVEDDATE",
    "body": "BODY"
}

class Rule:
    """
    Class for representing a rule as well as managing and creating queries based on rules. Generates WHERE clauses based
    on the fields, predicates and values present in a rule.
    """
    def __init__(self, field, predicate, value):
        self.field = field
        self.predicate = predicate
        self.value = value

    def build_query(self):
        if hasattr(self, self.predicate):
            query: str = getattr(self, self.predicate)()
            return query

        raise NotImplementedError(f"Predicate {self.predicate} is not implemented.")

    def contains(self):
        return f"{COLUMN_MAP[self.field]} LIKE '%{self.value}%'"

    def does_not_contain(self):
        return f"{COLUMN_MAP[self.field]} NOT LIKE '%{self.value}%'"

    def equals(self):
        return f"{COLUMN_MAP[self.field]} = '{self.value}'"

    def does_not_equal(self):
        return f"{COLUMN_MAP[self.field]} != '{self.value}'"

    def less_than_months(self):
         return f"{COLUMN_MAP[self.field]} > datetime('now', '-{self.value} months')"

    def greater_than_months(self):
         return f"{COLUMN_MAP[self.field]} < datetime('now', '-{self.value} months')"

    def less_than_days(self):
         return f"{COLUMN_MAP[self.field]} > datetime('now', '-{self.value} days')"

    def greater_than_days(self):
         return f"{COLUMN_MAP[self.field]} < datetime('now', '-{self.value} days')"


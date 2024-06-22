import env_utils
import logging
from pyairtable import Api
import pyairtable
from pyairtable.formulas import match

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class MyAirtable:
    def __init__(self):
        vars = env_utils.loadEnvVars(
            ["AIRTABLE_PAT", "AIRTABLE_TABLE_NAME", "AIRTABLE_BASE_ID"]
        )  # Get env vars
        self.connection = Api(vars["AIRTABLE_PAT"])
        self.table = self.connection.table(
            vars["AIRTABLE_BASE_ID"], vars["AIRTABLE_TABLE_NAME"]
        )

    def getMatchingRecords(
        self,
        match_formula: pyairtable.formulas.match = None,
        fields_to_return: list = None,
    ):
        """
        Description: getMatchingRecords return all the matching records based on the match_formula and fields_to_return
        Input:
            - match_formula: pyairtable.formulas.match; ref https://pyairtable.readthedocs.io/en/stable/api.html#module-pyairtable.formulas
            - fields_to_return: list; list of columns you'd want to be returned
        Output:
            - Iterator[List[RecordDict]] : Note that it'd return the RecordDict
        """
        return self.table.all(fields=fields_to_return, formula=match_formula)


if __name__ == "__main__":
    a = MyAirtable()
    # print(a.insertRecord("abcd","123", {}))
    t = a.getMatchingRecords(
        match_formula=match({"description": ""}), fields_to_return=["uid", "url"]
    )
    for x in t:
        print(x)
    # print(type(t))
    # print(t)
    # print(len(t))

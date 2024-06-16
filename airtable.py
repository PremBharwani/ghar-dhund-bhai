import env_utils
import logging
from pyairtable import Api
from pyairtable.formulas import match

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

"""
todo:
- create records
- update records with an id(groupId_postId)
""" 

class MyAirtable():
    def __init__(self):
        vars = env_utils.loadEnvVars(['AIRTABLE_PAT', 'AIRTABLE_TABLE_NAME', 'AIRTABLE_BASE_ID']) # Get env vars
        self.connection = Api(vars['AIRTABLE_PAT'])
        self.table = self.connection.table(vars['AIRTABLE_BASE_ID'], vars['AIRTABLE_TABLE_NAME'])

    def insertRecord(self, group_id: str, post_id: str, record: dict):
        """
        Inserts a record into the table.
        Returns: 1 -> successfully added. 0 -> already exists. -1 -> couldn't add the record
        """
        uid = group_id + "/" + post_id
        if(self.table.first(formula = match({'uid': uid})) is None):
            self.table.create({"uid": uid})
            return 1
        else:
            logger.info(f"insertRecord: record with {uid=} already exists")
            return 0

    def getAllRecords(self):
        return self.table.all()

if __name__=="__main__":
    a = MyAirtable()
    print(a.insertRecord("abcd","123", {}))
    print(a.getAllRecords())






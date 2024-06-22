import os
from selenium.webdriver.common.by import By
import time
import logging
from dotenv import load_dotenv
import scraper
import sys
import fb
import airtable
from pyairtable.formulas import match

URL = "https://facebook.com"
GROUP_ID = "320292845738195"

# Setup logging
# Defining handlers
fhandler = logging.FileHandler(filename="tmp.log")
shandler = logging.StreamHandler(stream=sys.stdout)
handlers = [fhandler, shandler]

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
    handlers=handlers,
)

logger = logging.getLogger(__name__)


def main():
    s = scraper.Scraper()
    root_window_id = s.initDriver()
    at = airtable.MyAirtable()
    fb.login(s)
    post_urls = fb.scrapeGroup(s, GROUP_ID)  # List of unique urls returned
    # for url in post_urls
    records = []  # Records to be added to the db
    for url in post_urls:
        d = {"uid": f"{GROUP_ID}/{url.split('/')[-1]}", "url": url}
        records.append(d)
    records_created = at.table.batch_create(records)
    logger.debug(f"main: {len(records_created)=} | {records_created=}")
    logger.info(
        f"main: added {len(records_created)} out of {len(records)} queued to be inserted"
    )
    unprocessed_records = at.getMatchingRecords(
        match_formula=match({"description": ""}), fields_to_return=["uid", "url"]
    )
    unprocessed_urls = [x["fields"]["url"] for x in unprocessed_records]  # List of urls
    logger.info(f"main: got {len(unprocessed_records)} records in airtable")

    post_descriptions = fb.extractPostDescriptions(s, unprocessed_urls)

    logger.debug(f"main: {post_descriptions=}")

    records_to_upsert = []

    for r in unprocessed_records:
        records_to_upsert.append(
            {
                "id": r["id"],
                "fields": {
                    "description": post_descriptions.get(
                        r["fields"]["url"], "No description available"
                    )
                },
            }
        )

    updated_records = at.table.batch_update(records_to_upsert)

    logger.info(
        f"main: {len(updated_records)} records out of {len(unprocessed_records)} queued were updated"
    )


if __name__ == "__main__":
    # main()
    main()

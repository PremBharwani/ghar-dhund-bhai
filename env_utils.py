from dotenv import load_dotenv
import os
import logging

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def loadEnvVars(keys: list):
    """
    loads env vars with keys from the .env file
    returns a dict with key value pair
    """
    load_dotenv()
    vals = {}
    for key in keys:
        val = os.environ.get(key)
        if val == None:
            logger.error(f"load_dotenv: couldn't find {key=} in the .env file")
            raise Exception(f"load_dotenv: couldn't find {key=} in the .env file")
        else:
            vals[key] = val
    return vals

"""
responsible for working with specifics related to facebook
login, check access, navigate to groups
"""
import logging
import sys
from dotenv import load_dotenv
from scraper import Scraper
from selenium.webdriver.common.by import By
import os
from bs4 import BeautifulSoup
import time

logger = logging.getLogger(__name__)

URL = "https://facebook.com"
N_TRIES = 5
SCROLL_SLEEP = 2  # seconds to sleep after scrolling
N_POSTS_TO_FETCH = 20
N_TABS = 10  # Num. of tabs to open simulatenously. Consider your machine's capability & set accordingly
POST_DESCRIPTION_XPATH = "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div[2]/div/div/div[4]/div/div/div/div/div/div/div[1]/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[3]/div[1]"
POST_IMAGES_XPATH = "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div[2]/div/div/div[4]/div/div/div/div/div/div/div[1]/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[3]/div[2]/div[1]"


def loadEnvVars():
    # TODO: Remove in favor of env_utils
    """
    loads FB_EMAIL, FB_PASS env vars from the .env file
    """
    load_dotenv()
    email = os.environ.get("FB_EMAIL")
    password = os.environ.get("FB_PASS")
    if email != None and password != None:
        logger.debug("loadEnvVars loaded env vars successfully")
        return (email, password)
    else:
        if email is None:
            logger.error(f"loadEnvVars couldn't find FB_EMAIL env var")
        if password is None:
            logger.error(f"loadEnvVars couldn't find FB_PASS env var")
        raise Exception(
            "loadEnvVars couldn't load FB_EMAIL and/or FB_PASS. Check logs."
        )


def login(scraper: Scraper):
    """
    logs into the facebook profile
    """
    (email, password) = loadEnvVars()
    scraper.navigateToUrl(URL)
    email_elem = scraper.findElemWhenClickable(By.XPATH, '//*[@id="email"]')
    email_elem.send_keys(email)
    password_elem = scraper.findElemWhenClickable(By.XPATH, '//*[@id="pass"]')
    password_elem.send_keys(password)
    go_btn = scraper.findElemWhenClickable(By.NAME, "login")
    go_btn.click()
    logger.debug("login: attempting to login")
    logger.debug(
        "login: checking access to home screen. i.e we've bypassed the security alert, etc. "
    )
    scraper.waitUntilElemAppears(
        By.XPATH,
        "/html/body/div[1]/div/div[1]/div/div[2]/div[3]/div/div/div/div/div/label/input",
        True,
    )


def __extractPostUrlsFromHtml(pg_src: str, group_id: str):
    """
    inputs:
        pg_src: source html
        group_id: fb group id that we're extracting
    outputs:
        posts: list of unique urls
    """
    bs = BeautifulSoup(pg_src, "html.parser")  # Parse html through bs
    a_tags = bs.find_all("a")
    posts = set()
    for x in a_tags:
        link = x.get("href")  # get the href
        if link is None:
            continue
        if f"{group_id}/posts/" in link:
            parts = link.split("/")
            post_id = parts[parts.index(group_id) + 2]
            posts.add(f"https://facebook.com/groups/{group_id}/posts/{post_id}")
    return list(posts)


def scrapeGroup(scraper: Scraper, group_id: str):
    """
    Scrape the posts of the group
    """
    scraper.navigateToUrl(
        f"https://www.facebook.com/groups/{group_id}/?sorting_setting=RECENT_ACTIVITY"
    )  # Navigate to the page using group id
    # Ensure that the page has loaded
    logger.info(
        "scrape_group: Ensuring the page has loaded by finding the 'Write something' span"
    )
    scraper.waitUntilElemAppears(
        By.XPATH,
        "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div[2]/div/div/div[4]/div/div[2]/div/div/div/div[1]/div/div/div/div[1]/div/div[1]/span",
    )
    logger.debug("scrapeGroup: going to sleep before scroll")
    time.sleep(SCROLL_SLEEP)
    while True:
        # logger.debug("scrapeGroup: scrolling down now")
        # Scroll down
        scraper.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_SLEEP)
        scraper.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_SLEEP)
        # scraper.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);");time.sleep(SCROLL_SLEEP)

        # logger.debug("scrapeGroup: fetching the page source to extract <a> tags with /groups/<group_id/posts/*")
        pg_src = scraper.driver.execute_script(
            "return document.documentElement.outerHTML"
        )  # Get the source and pass it through bs4
        posts = __extractPostUrlsFromHtml(pg_src, group_id)
        if len(posts) >= N_POSTS_TO_FETCH:
            break
        logger.info(
            f"scrapeGroup: found only {len(posts)} unique posts, needed {N_POSTS_TO_FETCH=} posts. Scrolling down to get more posts"
        )
    logger.info(f"scrapeGroup: found {len(posts)}")
    return list(posts)


def scrapePostDescriptionFromCurrentPage(scraper: Scraper) -> str:
    """
    scrapePost scrapes the details out of the post page, given that the page is already open on the active window!
    """
    scraper.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    text_elem = scraper.findElemWhenVisible(By.XPATH, POST_DESCRIPTION_XPATH)
    description = text_elem.text
    logger.info(f"scrapePostDescriptionFromCurrentPage: returned {description[:100]}")
    return description


def extractPostDescriptions(scraper: Scraper, post_urls: list[str]) -> dict:
    """
    Description: extracts the descriptions of all the post_urls supplied
    Input:
        - scraper: Scraper; Scraper object which is initialized
        - post_urls: list[str]; list of urls to be used to extract descriptions
    Output:
        - dict of url(key) to description(value)
    """
    post_descriptions = {}  # url(key) -> description(value)
    i = 0
    while i <= len(post_urls):
        scraper.switchToWindow(
            scraper.root_window_id
        )  # default switch to the root window
        logger.info(
            f"extractPostDescriptions: processing {min(i+N_TABS, len(post_urls))} / {len(post_urls)} urls"
        )
        active_window_ids = []
        windowid_url_map = {}
        # Open the first batch of the tabs
        batch_post_urls = post_urls[i : i + N_TABS]
        for (
            url
        ) in batch_post_urls:  # Just opening the windows and allowing each to load
            wid = scraper.createNewWindow(url)
            active_window_ids.append(wid)
            windowid_url_map[wid] = url
            logger.debug(f"extractPostDescriptions: created a window for {url}")

        time.sleep(2)
        # Start going to each page and extract the description. Further close the tabs then.
        # active_window_ids = list( set(scraper.driver.window_handles) - set(scraper.root_window_id) )
        for window_id in active_window_ids:
            # logger.info(f"extractPostDescriptions: switching to window {window_id=}")
            scraper.switchToWindow(window_id)
            time.sleep(2)
            desc = scrapePostDescriptionFromCurrentPage(scraper)
            post_descriptions[windowid_url_map[window_id]] = desc
            scraper.closeCurrentWindow()
        i = i + N_TABS

    return post_descriptions


if __name__ == "__main__":
    # Setup logging
    # Defining handlers
    handlers = []
    # fhandler = logging.FileHandler(filename="tmp.log"); handlers.append(fhandler)
    shandler = logging.StreamHandler(stream=sys.stdout)
    handlers.append(shandler)

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
        handlers=handlers,
    )
    ts = Scraper()

    ts.initDriver()
    login(ts)
    scrapeGroup(ts, "320292845738195")
    # scrapePost(ts, 'https://www.facebook.com/groups/320292845738195/posts/1102757397491732/')

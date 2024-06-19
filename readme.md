# ghar dhund bhai

in India, moving to an alien city for work could be daunting. moreover finding decent apartments/flats available for rent is difficult & needs you to go through the classic "flats and flatmates" groups on fb.

i am lazy to do that manually & i was bored enough to automate this :)

## usage
1. setup an airtable base and table. (for now create fields `uid`, `url`)
2. create the `.env` file referring to `env.example` provided
3. update the `GROUP_ID` variable in `main.py`. you can get the group id of the desired group from the url.
4. update the `N_POSTS_TO_FETCH` variable in `fb.py` to control how many posts to fetch in a single run. (default = 10)
5. finally run: `$ python main.py`

## todo

currently this repo is very raw & unorganized. i have planned a few features which i might implement if i could.

(my planned use case: cron scrapes various groups & populates my airtable with description, url, photos. could filter these records as per my location/preferences/etc. requirements)

[ ] integrate `scrapePostDescription` to automate updation of description values in airtable
[ ] download images & upload to airtable as attachments (helps me just go through the airtable sheet on my phone itself)

feel free to suggest & send pr's

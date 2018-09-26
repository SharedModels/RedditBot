import praw

reddit = praw.Reddit(
    client_id='mWL5DdszvyYpFA',
    client_secret='qE1SZZYxAk1V9AWD1FjhnI_0Lk4',
    user_agent='ScrapeyScraper')

askReddit = reddit.subreddit("askreddit")  # our current subreddit of interest


def collect(number, subreddit, filename):


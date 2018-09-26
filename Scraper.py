import praw

reddit = praw.Reddit(
    client_id='mWL5DdszvyYpFA',
    client_secret='qE1SZZYxAk1V9AWD1FjhnI_0Lk4',
    user_agent='ScrapeyScraper')

askReddit = "askreddit" # our current subreddit of interest
fileSaveSub = "submssions.csv"
fileSaveCom = "comments.csv"


def remove_line_break(text):
    return text.replace('\n', " ")


def submission_to_csv(number, subred, sub_csv, comments_csv):
    subreddit = reddit.subreddit(subred)
    with open(sub_csv, 'w') as s:
        for submission in subreddit.hot(limit=number):
            s.write(submission.id + '|' +
                    submission.title + '|' +
                    submission.author.name + '|' +
                    str(submission.score) + '|' +
                    remove_line_break(submission.selftext) + '|' +
                    submission.subreddit.display_name + '\n')
    s.close()
    with open(comments_csv, 'w') as c:
        for submission in subreddit.hot(limit=number):
            comments = submission.comments.list()
            for comment in comments:
                try:
                    c.write(comment.link_id + '|' +
                            comment.author.name + '|' +
                            str(comment.score) + '|' +
                            remove_line_break(comment.body) + '|' +
                            comment.parent_id + '\n')
                except:
                    continue
    c.close()


submission_to_csv(10, askReddit, fileSaveSub, fileSaveCom)

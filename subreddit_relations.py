import praw

class subreddit_relations():
    def __init__(self, subreddit_post_limit=10):
        self.subreddit_dict = {}
        self.comments_dict = {}
        self.subreddit_post_limit = subreddit_post_limit
        self.user_dict = {}
        self.reddit = praw.Reddit(
            client_id='mWL5DdszvyYpFA',
            client_secret='qE1SZZYxAk1V9AWD1FjhnI_0Lk4',
            user_agent='ScrapeyScraper')
        self.relations_dict = {}
        # self.sub_csv = sub_csv

    def retrieve_comments(self, subred):
        subreddit = self.reddit.subreddit(subred)
        subreddit_list = []
        for submission in subreddit.hot(limit=self.subreddit_post_limit):
            subreddit_list.append(submission.comments.list())
        self.comments_dict[subred] = subreddit_list

    def retrieve_users(self, subred):
        subreddit = self.reddit.subreddit(subred)
        user_list = []
        for comment_list in self.comments_dict[subred]:
            for comment in comment_list:
                user_list.append(comment.author.name)
        user_list = list(set(user_list))
        subreddit[subred] = user_list

    def retrieve_relations(self, subred):
        subreddit_relation_count = {}
        for user in self.user_dict[subred]:
            user_obj = self.reddit.redditor(user)
            for comment in user_obj.get_comments():
                if comment.subreddit in subreddit_relation_count.keys():
                    subreddit_relation_count[comment.subreddit] += 1
                else:
                    subreddit_relation_count[comment.subreddit] = 1

    def find_relations(self, subreddit_list):
        for subreddit in subreddit_list:
            self.retrieve_comments(subreddit)
            self.retrieve_users(subreddit)
            self.retrieve_relations(subreddit)
        return self.relations_dict


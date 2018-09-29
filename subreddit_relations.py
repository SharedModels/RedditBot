import praw
from multiprocessing.dummy import Pool as ThreadPool
import time


class SubredditRelations():
    def __init__(self, subreddit_post_limit=100):
        self.subreddit_dict = {}
        self.comments_dict = {}
        self.subreddit_post_limit = subreddit_post_limit
        self.user_dict = {}
        self.reddit = praw.Reddit(
            client_id='mWL5DdszvyYpFA',
            client_secret='qE1SZZYxAk1V9AWD1FjhnI_0Lk4',
            user_agent='ScrapeyScraper')
        self.relations_dict = {}
        self.current_subreddit = None
        self.subreddit_relation_count = {}
        # self.sub_csv = sub_csv

    def retrieve_comments(self, subred):
        subreddit = self.reddit.subreddit(subred)
        subreddit_list = []
        for submission in subreddit.hot(limit=self.subreddit_post_limit):
            subreddit_list.append(submission.comments.list())
        self.comments_dict[subred] = subreddit_list

    def retrieve_users(self, subred):
        user_list = []
        for comment_list in self.comments_dict[subred]:
            for comment in comment_list:
                try:
                    user_list.append(comment.author.name)
                except Exception as e:
                    # print(e)
                    continue
        user_list = list(set(user_list))
        self.user_dict[subred] = user_list

    def retrieve_relations(self, subred):
        subreddit_relation_count = {}
        for user in self.user_dict[subred]:
            try:
                user_obj = self.reddit.redditor(user)
                for comment in user_obj.comments.new(limit=10):
                    if comment.subreddit.display_name == subred:
                        continue
                    if comment.subreddit.display_name.lower() in subreddit_relation_count.keys():
                        subreddit_relation_count[comment.subreddit.display_name] += 1
                    else:
                        subreddit_relation_count[comment.subreddit.display_name] = 1
            except Exception as e:
                print(e)
                continue

        self.relations_dict[subred] = subreddit_relation_count

    def user_comments(self, user):
        try:
            user_obj = self.reddit.redditor(user)
            for comment in user_obj.comments.new(limit=10):
                if comment.subreddit.display_name == self.current_subreddit:
                    continue
                if comment.subreddit.display_name.lower() in self.subreddit_relation_count.keys():
                    self.subreddit_relation_count[comment.subreddit.display_name] += 1
                else:
                    self.subreddit_relation_count[comment.subreddit.display_name] = 1
        except Exception as e:
            time.sleep(10)
            print(e)


    def retrieve_relations_thread(self, subred):
        pool = ThreadPool(1000)
        self.subreddit_relation_count = {}
        self.current_subreddit = subred
        pool.map(self.user_comments, self.user_dict[subred])
        self.relations_dict[subred] = self.subreddit_relation_count

    def find_relations(self, subreddit_list):
        for subreddit in subreddit_list:
            self.retrieve_comments(subreddit)
            self.retrieve_users(subreddit)
            self.retrieve_relations_thread(subreddit)
        return self.relations_dict

    def top_100_subreddits(self, number = 100):
        subreddit = self.reddit.subreddit('all')
        top_100 = []
        for submission in subreddit.hot(limit=number):
            top_100.append(submission.subreddit.display_name)
        return list(set(top_100))

    # def find_relations_thread(self, subreddit_list):
    #     pool = ThreadPool(500)
    #     # for subreddit in subreddit_list:
    #     for subreddit in subreddit_list:
    #         self.retrieve_comments(subreddit)
    #         self.retrieve_users(subreddit)
    #     print(datetime.datetime.now())
    #     pool.map(self.retrieve_relations, subreddit_list)
    #
    #     return self.relations_dict



if __name__ == '__main__':
    import pandas as pd
    import datetime
    print(datetime.datetime.now())
    relations = SubredditRelations()
    subreddit_list = relations.top_100_subreddits(100)
    relations_dict = relations.find_relations(subreddit_list)
    print(datetime.datetime.now())
    relations_df = pd.DataFrame(relations_dict).fillna(0)
    print(relations_df)
    relations_df.to_csv('top_100_relations.csv')
    # print(relations.relations_dict)

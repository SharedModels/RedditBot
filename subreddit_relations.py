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
        self.pool = ThreadPool(500)
        self.subreddit_list = []
        self.global_user_list = []
        self.global_user_counts = {}
        self.relations_df_list = []

    def retrieve_submission_comments(self, submission):
        self.subreddit_list.append(submission.comments.list())

    def retrieve_comments(self, subred):
        subreddit = self.reddit.subreddit(subred)
        self.subreddit_list = []
        hot_posts = subreddit.hot(limit=self.subreddit_post_limit)
        self.pool.map(self.retrieve_submission_comments, hot_posts)
        self.comments_dict[subred] = self.subreddit_list

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

    def user_comments(self, user):
        current_user = {}
        try:
            user_obj = self.reddit.redditor(user)
            user_comments = user_obj.comments.new(limit=20)
            for comment in user_comments:
                if comment.subreddit.display_name.lower() in current_user.keys():
                    current_user[comment.subreddit.display_name] += 1
                else:
                    current_user[comment.subreddit.display_name] = 1
            self.global_user_counts[user] = current_user
        except Exception as e:
            self.global_user_counts[user] = current_user
            time.sleep(30)
            print(e)

    def combine_users(self, subreddit_list):
        for subreddit in subreddit_list:
            self.global_user_list += self.user_dict[subreddit]

    def combine_user_counts(self, subreddit):
        subreddit_user_counts = []
        for user in self.user_dict[subreddit]:
            subreddit_user_counts.append(self.global_user_counts[user])
        relations_df = pd.DataFrame(subreddit_user_counts).fillna(0).sum(axis=0)
        relations_df = relations_df.drop(subreddit)
        # print(relations_df)
        self.relations_df_list.append(relations_df)

    def find_relations(self, subreddit_list):
        for subreddit in subreddit_list:
            self.retrieve_comments(subreddit)
            self.retrieve_users(subreddit)
        self.combine_users(subreddit_list)
        self.pool.map(self.user_comments, self.global_user_list)
        for subreddit in subreddit_list:
            self.combine_user_counts(subreddit)
        combined_relations = pd.concat(self.relations_df_list, axis = 1)
        combined_relations.columns = subreddit_list
        return combined_relations

            # print(self.global_user_counts)
            # self.retrieve_relations_thread(subreddit)
            # pd.DataFrame(self.relations_dict).fillna(0).to_csv('top_100_relations.csv')
            # return self.relations_dict

    def top_100_subreddits(self, number=1000):
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
    subreddit_list = relations.top_100_subreddits(40)
    print(subreddit_list)
    relations_dict = relations.find_relations(subreddit_list)
    print(datetime.datetime.now())
    relations_df = pd.DataFrame(relations_dict).fillna(0)
    print(relations_df)
    relations_df.to_csv('top_100_relations.csv')
    # print(relations.relations_dict)

import subreddit_relations
import pandas as pd
import numpy as np
import praw

class CommentReply(subreddit_relations):
    def __init__(self,subreddit_post_limit=100):
        super().__init__(subreddit_post_limit=100)
        self.comment_reply_df = None

    @staticmethod
    def find_parent(df):
        map_df = df['body']
        map_df.index = df['id']
        df['parent_comment'] = df['parent_id'].map(map_df)
        return df

    def collect_comment_reply(self, subreddit):
        subred = self.reddit.subreddit(subreddit)
        comments = self.retrieve_comments(subred)
        comment_id_list = []
        for comment in comments:
            comment_id_dict = {}
            try:
                comment_id_dict['id'] = comment.id
                comment_id_dict['body'] = comment.body
                comment_id_dict['parent_id'] = comment.parent_id
                comment_id_dict['upvotes'] = comment.score
                comment_id_list.append(comment_id_dict)
            except Exception:
                continue
        comment_id_df = pd.DataFrame(comment_id_list)
        self.comment_reply_df = self.find_parent(comment_id_df)


if __name__ == '__main__':
    ComRep = CommentReply()
    subreddit = ComRep.reddit.subreddit("askreddit")
    ComRep.collect_comment_reply(subreddit)
    ComRep.comment_reply_df.to_csv('comment_reply_test.csv')

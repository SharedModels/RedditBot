from subreddit_relations import SubredditRelations
import pandas as pd
import numpy as np
import praw


class CommentReply(SubredditRelations):
    def __init__(self, subreddit_post_limit=100):
        super().__init__(subreddit_post_limit=subreddit_post_limit)
        self.comment_reply_df = None

    @staticmethod
    def find_parent(df):
        map_df = df['body']
        map_df.index = df['id']
        df['parent_map_id'] = df['parent_id'].str.lstrip('t1_')
        df['parent_comment'] = df['parent_map_id'].map(map_df)
        return df

    def collect_comment_reply(self, subreddit):
        # subred = self.reddit.subreddit(subreddit)
        comments = self.retrieve_comments(subreddit)
        comment_id_list = []
        for comment_list in comments:
            for comment in comment_list:
                comment_id_dict = {}
                try:
                    comment_id_dict['id'] = comment.id
                    comment_id_dict['body'] = comment.body
                    comment_id_dict['parent_id'] = comment.parent_id
                    comment_id_dict['upvotes'] = comment.score
                    comment_id_list.append(comment_id_dict)
                except Exception as e:
                    continue
        comment_id_df = pd.DataFrame(comment_id_list)
        # print(comment_id_df)
        self.comment_reply_df = self.find_parent(comment_id_df)
        self.comment_reply_df = self.comment_reply_df.dropna(axis = 0)
        return self.comment_reply_df


if __name__ == '__main__':
    ComRep = CommentReply()
    # subreddit = ComRep.reddit.subreddit("askreddit")
    ComRep.collect_comment_reply('askreddit')
    # ComRep.comment_reply_df.to_csv('comment_reply_test.csv')

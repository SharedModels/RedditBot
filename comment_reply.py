from subreddit_relations import SubredditRelations
import pandas as pd
import re


class CommentReply(SubredditRelations):
    def __init__(self, subreddit_post_limit=100):
        """
        Class to retrieve comments and turn it into comment - reply dataframe
        :param subreddit_post_limit: int
        """
        super().__init__(subreddit_post_limit=subreddit_post_limit)
        self.comment_reply_df = None

    @staticmethod
    def find_parent(df):
        """
        Map the parent comment in from parent id
        :param df: pandas DataFrame
        :return: pandas DataFrame
        """
        map_df = df['body']
        map_df.index = df['id']
        df['parent_map_id'] = df['parent_id'].str.lstrip('t1_')
        df = df.merge(df, left_on='parent_map_id', right_on='id', suffixes=['', '_parent'])

        # df['parent_comment'] = df['parent_map_id'].map(map_df)
        return df

    def collect_comment_reply(self, subreddit):
        """
        Retrieve comment body, parent and score for hot post limit posts in given subreddit
        :param subreddit: str
        :return: pandas DataFrame
        """
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
        self.comment_reply_df = self.comment_reply_df.dropna(axis=0)
        return self.comment_reply_df

    def collect_comment_reply_sentence_break(self, subreddit):
        """
        Same as class above, but breaks sentences up on fullstops and returns comment reply for every sentence in comment
        and parent comment.
        :param subreddit: str
        :return: pandas DataFrame
        """
        comments = self.retrieve_comments(subreddit)
        comment_id_list = []
        for comment_list in comments:
            for comment in comment_list:
                try:
                    for sentence in comment.body.split('.'):
                        comment_id_dict = {}
                        if len(sentence) < 5:
                            continue
                        comment_id_dict['id'] = comment.id
                        comment_id_dict['body'] = sentence
                        comment_id_dict['parent_id'] = comment.parent_id
                        comment_id_dict['upvotes'] = comment.score
                        comment_id_list.append(comment_id_dict)
                except Exception as e:
                    continue
        comment_id_df = pd.DataFrame(comment_id_list)
        # print(comment_id_df)
        self.comment_reply_df = self.find_parent(comment_id_df)
        self.comment_reply_df = self.comment_reply_df.dropna(axis=0)
        return self.comment_reply_df


if __name__ == '__main__':
    ComRep = CommentReply()
    # subreddit = ComRep.reddit.subreddit("askreddit")
    ComRep.collect_comment_reply('askreddit')
    # ComRep.comment_reply_df.to_csv('comment_reply_test.csv')

import subreddit_relations
import sklearn.feature_extraction.text as sktext
import pandas as pd
import numpy as np


def count(subred):
    subredditRelations = subreddit_relations.SubredditRelations()
    subredditRelations.retrieve_comments(subred)
    subredditRelations.retrieve_users(subred)

    comment_upvote = pd.DataFrame(subredditRelations.comment_upvote[subred])

    commentCol = comment_upvote["comment"]
    vec = sktext.CountVectorizer(stop_words="english", min_df=10, ngram_range=(1, 3))
    counts = vec.fit_transform(commentCol).todense()
    word_sum = counts.sum(axis=0)

    counts_multiplied = np.multiply(counts.T, comment_upvote["upvote"].values).T
    words_grouped = pd.DataFrame({'average_upvote': (counts_multiplied.sum(axis=0) / word_sum).tolist()[0],
                                  'counts': word_sum.tolist()[0]})#,
                                 #index=vec.get_feature_names())
    words_grouped.index = vec.get_feature_names()

    return words_grouped


count("The_Donald").to_csv("count_the_donald.csv")

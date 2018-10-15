import subreddit_relations
import sklearn.feature_extraction.text as sktext
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split


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
                                  'counts': word_sum.tolist()[0]})  # ,
    # index=vec.get_feature_names())
    words_grouped.index = vec.get_feature_names()

    return words_grouped


subredditRelations = subreddit_relations.SubredditRelations()
subredditRelations.retrieve_comments('askreddit')
subredditRelations.retrieve_users('askreddit')

comment_upvote = pd.DataFrame(subredditRelations.comment_upvote['askreddit'])
clf = RandomForestRegressor()
vec = sktext.CountVectorizer(ngram_range=(1, 3), min_df = 5)
# train_X = comment_upvote.sample()

idx = np.random.choice(comment_upvote.index.values, round(len(comment_upvote) * 0.66), False)

train = comment_upvote.iloc[idx, :]
test = comment_upvote.iloc[~idx, :]

train_X = vec.fit_transform(train['comment'])
train_y = train['upvote']
test_X = vec.transform(test['comment'])
test_y = test['upvote']

# train_X, test_X, train_y, test_y = train_test_split(comment_upvote['comment'], comment_upvote['upvote'])

clf.fit(train_X, train_y)
pred_csv = test
pred_csv['predictions'] = clf.predict(test_X)
# pred_csv['abs_predictions'] = pred_csv['predictions'].abs()
pred_csv['abs_error'] = (pred_csv['upvote'] - pred_csv['predictions']).abs()
print(pred_csv.median())
pred_csv.to_csv('reddit_preds.csv')

# print(clf.score(test_X, test_y))

# print(comment_upvote.head())

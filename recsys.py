import os
import pandas as pd
import numpy as np
import sklearn.preprocessing
import scrapbook as sb
import math
import sqlite3

import recommenders.models.wide_deep.wide_deep_utils as wide_deep
import recommenders.evaluation.python_evaluation as evaluator

from recommenders.utils import plot
from sklearn.model_selection import train_test_split
from recommenders.datasets.python_splitters import python_random_split
from recommenders.utils import tf_utils
from recommenders.datasets.pandas_df_utils import user_item_pairs

USER_COL = "userID"
ITEM_COL = "itemID"
RATING_COL = "rating"
ITEM_FEAT_COL = "genre"
PREDICT_COL = "prediction"

con = sqlite3.connect("admin.db")
movie_df = pd.read_sql_query(
    """select * from Movies""", con
)
rating_df = pd.read_sql_query(
    """select * from Ratings""", con
)
tag_df = pd.read_sql_query(
    """select * from Tags""", con
)
links_df = pd.read_sql_query(
    """select * from Links""", con
)
con.close()

movie_df = movie_df.iloc[1:, :]
rating_df = rating_df.iloc[1:, :]
tag_df = tag_df.iloc[1:, :]
links_df = links_df.iloc[1:, :]

movie_df = movie_df.astype({'movieId': 'int'})
rating_df = rating_df.astype(
    {'userId': 'int', 'movieId': 'int', 'rating': 'float'})
tag_df = tag_df.astype({'userId': 'int', 'movieId': 'int'})
links_df = links_df.astype({'movieId': 'int', 'imdbId': 'int'})

# Rating 추가 로직

new_ratings = rating_df

new_ratings = new_ratings.groupby(['movieId']).count(
).reset_index().sort_values('rating', ascending=False)[['movieId', 'rating']]
new_ratings.columns = ['movieId', 'count']

new_rating_movies = movie_df

binarizer = sklearn.preprocessing.MultiLabelBinarizer()

new_rating_genre_df = pd.DataFrame(binarizer.fit_transform(
    new_rating_movies['genres'].apply(lambda x: x.split("|"))
))

new_rating_genre_df.columns = list(binarizer.classes_)
new_rating_movies = new_rating_movies.drop(['genres'], axis=1)
new_rating_movies = new_rating_movies.set_index(keys=np.arange(9742))
new_rating_movies = pd.concat([new_rating_movies, new_rating_genre_df], axis=1)
new_rating_movies = pd.merge(
    new_rating_movies, new_ratings, left_on='movieId', right_on='movieId', how='left')
new_rating_movies = new_rating_movies.replace(np.nan, 0)

new_rating_genres = list(binarizer.classes_)

new_rating_movies_by_genre = {}
for genre in new_rating_genre_df.columns:
    new_rating_movies_by_genre[genre] = new_rating_movies[new_rating_movies[genre] == 1].sort_values(['count'], ascending=False)[[
        'title', 'movieId']].to_dict('records')

new_rating_users = rating_df.drop_duplicates(
    'userId')[['userId']].reset_index(drop=True)
new_rating_userId = new_rating_users.size + 1

# --------------

temp_movie_df = links_df[['movieId', 'imdbId']]
temp_movie_df.columns = ['itemID', 'imdbID']
movie_dict = temp_movie_df.set_index('itemID').to_dict('index')

data = pd.merge(movie_df, rating_df, on=['movieId'], how='inner')
data = data.drop(['title', 'timestamp'], axis=1)
data = data[['userId', 'movieId', 'rating', 'genres']]
data.columns = [USER_COL, ITEM_COL, RATING_COL, ITEM_FEAT_COL]

genres_encoder = sklearn.preprocessing.MultiLabelBinarizer()
data[ITEM_FEAT_COL] = genres_encoder.fit_transform(
    data[ITEM_FEAT_COL].apply(lambda x: x.split("|"))
).tolist()

train, test = python_random_split(data, ratio=0.8, seed=42)

items = data.drop_duplicates(
    ITEM_COL)[[ITEM_COL, ITEM_FEAT_COL]].reset_index(drop=True)
users = data.drop_duplicates(USER_COL)[[USER_COL]].reset_index(drop=True)

wide_columns, deep_columns = wide_deep.build_feature_columns(
    model_type='wide_deep',
    user_col=USER_COL,
    users=users[USER_COL].values,
    user_dim=16,
    item_col=ITEM_COL,
    items=items[ITEM_COL].values,
    item_dim=16,
    item_feat_col=ITEM_FEAT_COL,
    item_feat_shape=len(items[ITEM_FEAT_COL][0]),
)

model = wide_deep.build_model(
    model_dir='./models',
    wide_columns=wide_columns,
    deep_columns=deep_columns,
    dnn_hidden_units=[64, 128, 512],
    dnn_dropout=0.4,
    seed=42
)

RANKING_METRICS = [
    evaluator.ndcg_at_k.__name__,
    evaluator.precision_at_k.__name__,
]
RATING_METRICS = [
    evaluator.rmse.__name__,
    evaluator.mae.__name__,
]

cols = {
    'col_user': USER_COL,
    'col_item': ITEM_COL,
    'col_rating': RATING_COL,
    'col_prediction': PREDICT_COL,
}

ranking_pool = user_item_pairs(
    user_df=users,
    item_df=items,
    user_col=USER_COL,
    item_col=ITEM_COL,
    user_item_filter_df=train,
    shuffle=True,
    seed=42
)

train_fn = tf_utils.pandas_input_fn(
    df=train,
    y_col=RATING_COL,
    num_epochs=None,
    shuffle=True,
    seed=42,
)

model.train(
    input_fn=train_fn,
    steps=30000
)

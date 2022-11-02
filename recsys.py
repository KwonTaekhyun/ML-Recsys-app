import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sklearn.preprocessing
import tensorflow as tf
import scrapbook as sb
import math

from recommenders.datasets.python_splitters import python_random_split
import recommenders.evaluation.python_evaluation as evaluator
import recommenders.models.wide_deep.wide_deep_utils as wide_deep
from recommenders.utils import tf_utils
from recommenders.datasets.pandas_df_utils import user_item_pairs
from recommenders.utils import plot

USER_COL = "userID"
ITEM_COL = "itemID"
RATING_COL = "rating"
ITEM_FEAT_COL = "genre"
PREDICT_COL = "prediction"
SEED = 42

TOP_K = 10
BATCH_SIZE = 16
STEPS = 50000

movie_df = pd.read_csv('./ml-latest-small/movies.csv')
rating_df = pd.read_csv('./ml-latest-small/ratings.csv')
tag_df = pd.read_csv('./ml-latest-small/tags.csv')

data = pd.merge(movie_df, rating_df, on=['movieId'], how='inner')
data = data.drop(['title', 'timestamp'], axis=1)
data = data[['userId', 'movieId', 'rating', 'genres']]
data.columns = [USER_COL, ITEM_COL, RATING_COL, ITEM_FEAT_COL]

temp_movie_df = movie_df[['movieId', 'title']]
temp_movie_df.columns = ['itemID', 'title']
movie_dict = temp_movie_df.set_index('itemID').to_dict('index')

genres_encoder = sklearn.preprocessing.MultiLabelBinarizer()
data[ITEM_FEAT_COL] = genres_encoder.fit_transform(
    data[ITEM_FEAT_COL].apply(lambda x: x.split("|"))
).tolist()

train, test = python_random_split(data, ratio=0.75, seed=42)

items = data.drop_duplicates(
    ITEM_COL)[[ITEM_COL, ITEM_FEAT_COL]].reset_index(drop=True)
item_feat_shape = len(items[ITEM_FEAT_COL][0])
users = data.drop_duplicates(USER_COL)[[USER_COL]].reset_index(drop=True)

wide_columns, deep_columns = wide_deep.build_feature_columns(
    model_type='wide_deep',
    user_col=USER_COL,
    users=users[USER_COL].values,
    user_dim=32,
    item_col=ITEM_COL,
    items=items[ITEM_COL].values,
    item_dim=16,
    item_feat_col=ITEM_FEAT_COL,
    item_feat_shape=item_feat_shape,
)

model = wide_deep.build_model(
    model_dir='./models',
    wide_columns=wide_columns,
    deep_columns=deep_columns,
    linear_optimizer=tf_utils.build_optimizer('adagrad', 0.0621, **{
        'l1_regularization_strength': 0.0,
        'l2_regularization_strength': 0.0,
        'momentum': 0.0,
    }),
    dnn_optimizer=tf_utils.build_optimizer('adadelta', 0.1, **{
        'l1_regularization_strength': 0.0,
        'l2_regularization_strength': 0.0,
        'momentum': 0.0,
    }),
    dnn_hidden_units=[h for h in [0, 64, 128, 512] if h > 0],
    dnn_dropout=0.8,
    dnn_batch_norm=(1 == 1),
    log_every_n_iter=10000,
    save_checkpoints_steps=10000,
    seed=SEED
)

cols = {
    'col_user': USER_COL,
    'col_item': ITEM_COL,
    'col_rating': RATING_COL,
    'col_prediction': PREDICT_COL,
}

# Prepare ranking evaluation set, i.e. get the cross join of all user-item pairs
ranking_pool = user_item_pairs(
    user_df=users,
    item_df=items,
    user_col=USER_COL,
    item_col=ITEM_COL,
    user_item_filter_df=train,
    shuffle=True,
    seed=SEED
)

RANKING_METRICS = [
    evaluator.ndcg_at_k.__name__,
    evaluator.precision_at_k.__name__,
]
RATING_METRICS = [
    evaluator.rmse.__name__,
    evaluator.mae.__name__,
]

train_fn = tf_utils.pandas_input_fn(
    df=train,
    y_col=RATING_COL,
    batch_size=BATCH_SIZE,
    num_epochs=None,
    shuffle=True,
    seed=SEED,
)

model.train(
    input_fn=train_fn,
    steps=STEPS
)

if len(RATING_METRICS) > 0:
    predictions = list(model.predict(
        input_fn=tf_utils.pandas_input_fn(df=test)))
    prediction_df = test.drop(RATING_COL, axis=1)
    prediction_df[PREDICT_COL] = [p['predictions'][0] for p in predictions]

    rating_results = {}
    for m in RATING_METRICS:
        result = evaluator.metrics[m](test, prediction_df, **cols)
        sb.glue(m, result)
        rating_results[m] = result
    print(rating_results)

predict_movies = prediction_df[prediction_df['userID'] == 417].sort_values(
    by=['prediction'], ascending=False).iloc[0:10]['itemID'].apply(lambda x: movie_dict[x]['title'])

print(predict_movies)

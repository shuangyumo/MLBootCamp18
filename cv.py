from __future__ import unicode_literals
import gc

from sklearn.metrics import roc_auc_score
from skopt import BayesSearchCV
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.pipeline import Pipeline, FeatureUnion
from lightgbm import LGBMClassifier
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder
import os
from datetime import datetime

from adversial_validation import adversial_train_test_split
from data_loading import load_csi_test, load_csi_train, load_features
from data_prepare import merge_features, add_weekday, add_holidays, features, categorical
from transformers.pandas_select import PandasSelect
from transformers.pandas_subset import PandasSubset

os.environ['MKL_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'

target = 'CSI'

search_spaces = {
    'subset__COM_CAT#1': [True, False],
    # 'subset__COM_CAT#2': [True, False],
    'subset__COM_CAT#3': [True, False],
    'subset__BASE_TYPE': [True, False],
    # 'subset__ACT': [True, False],
    # 'subset__ARPU_GROUP': [True, False],
    'subset__COM_CAT#7': [True, False],
    # 'subset__COM_CAT#8': [True, False],
    'subset__DEVICE_TYPE_ID': [True, False],
    # 'subset__INTERNET_TYPE_ID': [True, False],
    'subset__REVENUE': [True, False],
    'subset__ITC': [True, False],
    'subset__VAS': [True, False],
    'subset__RENT_CHANNEL': [True, False],
    'subset__ROAM': [True, False],
    'subset__COST': [True, False],
    'subset__COM_CAT#17': [True, False],
    'subset__COM_CAT#18': [True, False],
    'subset__COM_CAT#19': [True, False],
    'subset__COM_CAT#20': [True, False],
    'subset__COM_CAT#21': [True, False],
    'subset__COM_CAT#22': [True, False],
    # 'subset__COM_CAT#23': [True, False],
    'subset__COM_CAT#25': [True, False],
    'subset__COM_CAT#26': [True, False],
    'subset__COM_CAT#27': [True, False],
    'subset__COM_CAT#28': [True, False],
    'subset__COM_CAT#29': [True, False],
    # 'subset__COM_CAT#30': [True, False],
    'subset__COM_CAT#31': [True, False],
    # 'subset__COM_CAT#32': [True, False],
    'subset__COM_CAT#33': [True, False],
    # 'subset__COM_CAT#34': [True, False],

    # 'subset__CONTACT_DATE_WEEKDAY': [True, False],

    # 'subset__CONTACT_DATE_0_HOLIDAYS': [True, False],
    # 'subset__CONTACT_DATE_1_HOLIDAYS': [True, False],
    # 'subset__CONTACT_DATE_2_HOLIDAYS': [True, False],
    # 'subset__CONTACT_DATE_3_HOLIDAYS': [True, False],

    'subset__REVENUE_2m': [True, False],
    'subset__ITC_2m': [True, False],
    # 'subset__VAS_2m': [True, False],
    'subset__RENT_CHANNEL_2m': [True, False],
    'subset__ROAM_2m': [True, False],
    'subset__COST_2m': [True, False],
    # 'subset__COM_CAT#17_2m': [True, False],
    'subset__COM_CAT#18_2m': [True, False],
    'subset__COM_CAT#19_2m': [True, False],
    'subset__COM_CAT#20_2m': [True, False],
    'subset__COM_CAT#21_2m': [True, False],
    'subset__COM_CAT#22_2m': [True, False],
    'subset__COM_CAT#23_2m': [True, False],
    'subset__COM_CAT#27_2m': [True, False],
    'subset__COM_CAT#28_2m': [True, False],
    'subset__COM_CAT#29_2m': [True, False],
    'subset__COM_CAT#30_2m': [True, False],
    'subset__COM_CAT#31_2m': [True, False],
    # 'subset__COM_CAT#32_2m': [True, False],
    'subset__COM_CAT#33_2m': [True, False],

    'subset__REVENUE_3m': [True, False],
    # 'subset__ITC_3m': [True, False],
    # 'subset__VAS_3m': [True, False],
    'subset__RENT_CHANNEL_3m': [True, False],
    'subset__ROAM_3m': [True, False],
    'subset__COST_3m': [True, False],
    'subset__COM_CAT#17_3m': [True, False],
    # 'subset__COM_CAT#18_3m': [True, False],
    'subset__COM_CAT#19_3m': [True, False],
    'subset__COM_CAT#20_3m': [True, False],
    'subset__COM_CAT#21_3m': [True, False],
    # 'subset__COM_CAT#22_3m': [True, False],
    'subset__COM_CAT#23_3m': [True, False],
    # 'subset__COM_CAT#27_3m': [True, False],
    'subset__COM_CAT#28_3m': [True, False],
    # 'subset__COM_CAT#29_3m': [True, False],
    'subset__COM_CAT#30_3m': [True, False],
    'subset__COM_CAT#31_3m': [True, False],
    # 'subset__COM_CAT#32_3m': [True, False],
    # 'subset__COM_CAT#33_3m': [True, False],

    'subset__REVENUE_6m': [True, False],
    # 'subset__ITC_6m': [True, False],
    'subset__VAS_6m': [True, False],
    'subset__RENT_CHANNEL_6m': [True, False],
    'subset__ROAM_6m': [True, False],
    'subset__COST_6m': [True, False],
    'subset__COM_CAT#17_6m': [True, False],
    'subset__COM_CAT#18_6m': [True, False],
    'subset__COM_CAT#19_6m': [True, False],
    'subset__COM_CAT#20_6m': [True, False],
    'subset__COM_CAT#21_6m': [True, False],
    # 'subset__COM_CAT#22_6m': [True, False],
    # 'subset__COM_CAT#23_6m': [True, False],
    # 'subset__COM_CAT#27_6m': [True, False],
    # 'subset__COM_CAT#28_6m': [True, False],
    'subset__COM_CAT#29_6m': [True, False],
    'subset__COM_CAT#30_6m': [True, False],
    'subset__COM_CAT#31_6m': [True, False],
    'subset__COM_CAT#32_6m': [True, False],
    # 'subset__COM_CAT#33_6m': [True, False],

    'subset__REVENUE_diff_1m': [True, False],
    'subset__ITC_diff_1m': [True, False],
    'subset__VAS_diff_1m': [True, False],
    'subset__RENT_CHANNEL_diff_1m': [True, False],
    'subset__ROAM_diff_1m': [True, False],
    'subset__COST_diff_1m': [True, False],
    'subset__COM_CAT#17_diff_1m': [True, False],
    # 'subset__COM_CAT#18_diff_1m': [True, False],
    'subset__COM_CAT#19_diff_1m': [True, False],
    'subset__COM_CAT#20_diff_1m': [True, False],
    'subset__COM_CAT#21_diff_1m': [True, False],
    'subset__COM_CAT#22_diff_1m': [True, False],
    'subset__COM_CAT#23_diff_1m': [True, False],
    'subset__COM_CAT#27_diff_1m': [True, False],
    # 'subset__COM_CAT#28_diff_1m': [True, False],
    'subset__COM_CAT#29_diff_1m': [True, False],
    'subset__COM_CAT#30_diff_1m': [True, False],
    'subset__COM_CAT#31_diff_1m': [True, False],
    'subset__COM_CAT#32_diff_1m': [True, False],
    'subset__COM_CAT#33_diff_1m': [True, False],

    'subset__REVENUE_diff_2m': [True, False],
    # 'subset__ITC_diff_2m': [True, False],
    'subset__VAS_diff_2m': [True, False],
    'subset__RENT_CHANNEL_diff_2m': [True, False],
    # 'subset__ROAM_diff_2m': [True, False],
    'subset__COST_diff_2m': [True, False],
    'subset__COM_CAT#17_diff_2m': [True, False],
    'subset__COM_CAT#18_diff_2m': [True, False],
    # 'subset__COM_CAT#19_diff_2m': [True, False],
    # 'subset__COM_CAT#20_diff_2m': [True, False],
    # 'subset__COM_CAT#21_diff_2m': [True, False],
    'subset__COM_CAT#22_diff_2m': [True, False],
    'subset__COM_CAT#23_diff_2m': [True, False],
    # 'subset__COM_CAT#27_diff_2m': [True, False],
    # 'subset__COM_CAT#28_diff_2m': [True, False],
    'subset__COM_CAT#29_diff_2m': [True, False],
    # 'subset__COM_CAT#30_diff_2m': [True, False],
    # 'subset__COM_CAT#31_diff_2m': [True, False],
    'subset__COM_CAT#32_diff_2m': [True, False],
    'subset__COM_CAT#33_diff_2m': [True, False],

    'subset__REVENUE_diff_3m': [True, False],
    # 'subset__ITC_diff_3m': [True, False],
    'subset__VAS_diff_3m': [True, False],
    'subset__RENT_CHANNEL_diff_3m': [True, False],
    'subset__ROAM_diff_3m': [True, False],
    'subset__COST_diff_3m': [True, False],
    'subset__COM_CAT#17_diff_3m': [True, False],
    # 'subset__COM_CAT#18_diff_3m': [True, False],
    'subset__COM_CAT#19_diff_3m': [True, False],
    # 'subset__COM_CAT#20_diff_3m': [True, False],
    'subset__COM_CAT#21_diff_3m': [True, False],
    'subset__COM_CAT#22_diff_3m': [True, False],
    'subset__COM_CAT#23_diff_3m': [True, False],
    # 'subset__COM_CAT#27_diff_3m': [True, False],
    # 'subset__COM_CAT#28_diff_3m': [True, False],
    # 'subset__COM_CAT#29_diff_3m': [True, False],
    # 'subset__COM_CAT#30_diff_3m': [True, False],
    # 'subset__COM_CAT#31_diff_3m': [True, False],
    'subset__COM_CAT#32_diff_3m': [True, False],
    'subset__COM_CAT#33_diff_3m': [True, False],

    # 'estimator__C': (0.01, 1.0, 'log-uniform'),

    # 'lgb__num_leaves': (3, 21),
    # # 'lgb__n_estimators': (1, 100),
    # 'lgb__max_depth': (2, 50),
    # 'lgb__min_child_samples': (1, 500),
    # 'lgb__max_bin': (10, 2000),
    # 'lgb__subsample': (0.1, 1.0, 'uniform'),
    # 'lgb__subsample_freq': (0, 10),
    # 'lgb__colsample_bytree': (0.5, 1.0, 'uniform'),
    # 'lgb__min_child_weight': (0, 50),
    # 'lgb__subsample_for_bin': (100000, 500000),
    # 'lgb__reg_lambda': (1e-9, 1000, 'log-uniform'),
    # 'lgb__reg_alpha': (1e-9, 1.0, 'log-uniform'),
}

ppl = Pipeline([
    ('subset', PandasSubset(**{k: True for k in features})),
    ('vectorizer', FeatureUnion([
        ('REVENUE', PandasSelect('REVENUE', fillna_zero=True)),
        ('ITC', PandasSelect('ITC', fillna_zero=True)),
        ('VAS', PandasSelect('VAS', fillna_zero=True)),
        ('RENT_CHANNEL', PandasSelect('RENT_CHANNEL', fillna_zero=True)),
        ('ROAM', PandasSelect('ROAM', fillna_zero=True)),
        ('COST', PandasSelect('COST', fillna_zero=True)),
        ('COM_CAT#17', PandasSelect('COM_CAT#17', fillna_zero=True)),
        ('COM_CAT#18', PandasSelect('COM_CAT#18', fillna_zero=True)),
        ('COM_CAT#19', PandasSelect('COM_CAT#19', fillna_zero=True)),
        ('COM_CAT#20', PandasSelect('COM_CAT#20', fillna_zero=True)),
        ('COM_CAT#21', PandasSelect('COM_CAT#21', fillna_zero=True)),
        ('COM_CAT#22', PandasSelect('COM_CAT#22', fillna_zero=True)),
        # ('COM_CAT#23', PandasSelect('COM_CAT#23', fillna_zero=True)),
        ('COM_CAT#27', PandasSelect('COM_CAT#27', fillna_zero=True)),
        ('COM_CAT#28', PandasSelect('COM_CAT#28', fillna_zero=True)),
        ('COM_CAT#29', PandasSelect('COM_CAT#29', fillna_zero=True)),
        # ('COM_CAT#30', PandasSelect('COM_CAT#30', fillna_zero=True)),
        ('COM_CAT#31', PandasSelect('COM_CAT#31', fillna_zero=True)),
        # ('COM_CAT#32', PandasSelect('COM_CAT#32', fillna_zero=True)),
        ('COM_CAT#33', PandasSelect('COM_CAT#33', fillna_zero=True)),

        ('COM_CAT#1', Pipeline([
            ('select', PandasSelect('COM_CAT#1', fillna_zero=True)),
            ('ohe', OneHotEncoder(handle_unknown='ignore', sparse=False))
        ])),
        # ('COM_CAT#2', Pipeline([
        #     ('select', PandasSelect('COM_CAT#2', fillna_zero=True)),
        #     ('ohe', OneHotEncoder(handle_unknown='ignore', sparse=False))
        # ])),
        ('COM_CAT#3', Pipeline([
            ('select', PandasSelect('COM_CAT#3', fillna_zero=True)),
            ('ohe', OneHotEncoder(handle_unknown='ignore', sparse=False))
        ])),
        ('BASE_TYPE', Pipeline([
            ('select', PandasSelect('BASE_TYPE', fillna_zero=True)),
            ('ohe', OneHotEncoder(handle_unknown='ignore', sparse=False))
        ])),
        # ('ACT', Pipeline([
        #     ('select', PandasSelect('ACT', fillna_zero=True)),
        #     ('ohe', OneHotEncoder(handle_unknown='ignore', sparse=False))
        # ])),
        # ('ARPU_GROUP', Pipeline([
        #     ('select', PandasSelect('ARPU_GROUP', fillna_zero=True)),
        #     ('ohe', OneHotEncoder(handle_unknown='ignore', sparse=False))
        # ])),
        ('COM_CAT#7', Pipeline([
            ('select', PandasSelect('COM_CAT#7', fillna_zero=True)),
            ('ohe', OneHotEncoder(handle_unknown='ignore', sparse=False))
        ])),
        # ('COM_CAT#8', Pipeline([
        #     ('select', PandasSelect('COM_CAT#8', fillna_zero=True)),
        #     ('ohe', OneHotEncoder(handle_unknown='ignore', sparse=False))
        # ])),
        ('DEVICE_TYPE_ID', Pipeline([
            ('select', PandasSelect('DEVICE_TYPE_ID', fillna_zero=True)),
            ('ohe', OneHotEncoder(handle_unknown='ignore', sparse=False))
        ])),
        # ('INTERNET_TYPE_ID', Pipeline([
        #     ('select', PandasSelect('INTERNET_TYPE_ID', fillna_zero=True)),
        #     ('ohe', OneHotEncoder(handle_unknown='ignore', sparse=False))
        # ])),
        ('COM_CAT#25', Pipeline([
            ('select', PandasSelect('COM_CAT#25', fillna_zero=True)),
            ('ohe', OneHotEncoder(handle_unknown='ignore', sparse=False))
        ])),
        ('COM_CAT#26', Pipeline([
            ('select', PandasSelect('COM_CAT#26', fillna_zero=True)),
            ('ohe', OneHotEncoder(handle_unknown='ignore', sparse=False))
        ])),
        # ('COM_CAT#34', Pipeline([
        #     ('select', PandasSelect('COM_CAT#34', fillna_zero=True)),
        #     ('ohe', OneHotEncoder(handle_unknown='ignore', sparse=False))
        # ])),

        # ('CONTACT_DATE_WEEKDAY', Pipeline([
        #     ('select', PandasSelect('CONTACT_DATE_WEEKDAY', fillna_zero=True)),
        #     ('ohe', OneHotEncoder(handle_unknown='ignore', sparse=False))
        # ])),

        # ('CONTACT_DATE_0_HOLIDAYS', Pipeline([
        #     ('select', PandasSelect('CONTACT_DATE_0_HOLIDAYS', fillna_zero=True)),
        #     ('ohe', OneHotEncoder(handle_unknown='ignore', sparse=False))
        # ])),
        # ('CONTACT_DATE_1_HOLIDAYS', Pipeline([
        #     ('select', PandasSelect('CONTACT_DATE_1_HOLIDAYS', fillna_zero=True)),
        #     ('ohe', OneHotEncoder(handle_unknown='ignore', sparse=False))
        # ])),
        # ('CONTACT_DATE_2_HOLIDAYS', Pipeline([
        #     ('select', PandasSelect('CONTACT_DATE_2_HOLIDAYS', fillna_zero=True)),
        #     ('ohe', OneHotEncoder(handle_unknown='ignore', sparse=False))
        # ])),
        # ('CONTACT_DATE_3_HOLIDAYS', Pipeline([
        #     ('select', PandasSelect('CONTACT_DATE_2_HOLIDAYS', fillna_zero=True)),
        #     ('ohe', OneHotEncoder(handle_unknown='ignore', sparse=False))
        # ])),

        ('REVENUE_2m', PandasSelect('REVENUE_2m', fillna_zero=True)),
        ('ITC_2m', PandasSelect('ITC_2m', fillna_zero=True)),
        # ('VAS_2m', PandasSelect('VAS_2m', fillna_zero=True)),
        ('RENT_CHANNEL_2m', PandasSelect('RENT_CHANNEL_2m', fillna_zero=True)),
        ('ROAM_2m', PandasSelect('ROAM_2m', fillna_zero=True)),
        ('COST_2m', PandasSelect('COST_2m', fillna_zero=True)),
        # ('COM_CAT#17_2m', PandasSelect('COM_CAT#17_2m', fillna_zero=True)),
        ('COM_CAT#18_2m', PandasSelect('COM_CAT#18_2m', fillna_zero=True)),
        ('COM_CAT#19_2m', PandasSelect('COM_CAT#19_2m', fillna_zero=True)),
        ('COM_CAT#20_2m', PandasSelect('COM_CAT#20_2m', fillna_zero=True)),
        ('COM_CAT#21_2m', PandasSelect('COM_CAT#21_2m', fillna_zero=True)),
        ('COM_CAT#22_2m', PandasSelect('COM_CAT#22_2m', fillna_zero=True)),
        ('COM_CAT#23_2m', PandasSelect('COM_CAT#23_2m', fillna_zero=True)),
        ('COM_CAT#27_2m', PandasSelect('COM_CAT#27_2m', fillna_zero=True)),
        ('COM_CAT#28_2m', PandasSelect('COM_CAT#28_2m', fillna_zero=True)),
        ('COM_CAT#29_2m', PandasSelect('COM_CAT#29_2m', fillna_zero=True)),
        ('COM_CAT#30_2m', PandasSelect('COM_CAT#30_2m', fillna_zero=True)),
        ('COM_CAT#31_2m', PandasSelect('COM_CAT#31_2m', fillna_zero=True)),
        # ('COM_CAT#32_2m', PandasSelect('COM_CAT#32_2m', fillna_zero=True)),
        ('COM_CAT#33_2m', PandasSelect('COM_CAT#33_2m', fillna_zero=True)),

        ('REVENUE_3m', PandasSelect('REVENUE_3m', fillna_zero=True)),
        # ('ITC_3m', PandasSelect('ITC_3m', fillna_zero=True)),
        # ('VAS_3m', PandasSelect('VAS_3m', fillna_zero=True)),
        ('RENT_CHANNEL_3m', PandasSelect('RENT_CHANNEL_3m', fillna_zero=True)),
        ('ROAM_3m', PandasSelect('ROAM_3m', fillna_zero=True)),
        ('COST_3m', PandasSelect('COST_3m', fillna_zero=True)),
        ('COM_CAT#17_3m', PandasSelect('COM_CAT#17_3m', fillna_zero=True)),
        # ('COM_CAT#18_3m', PandasSelect('COM_CAT#18_3m', fillna_zero=True)),
        ('COM_CAT#19_3m', PandasSelect('COM_CAT#19_3m', fillna_zero=True)),
        ('COM_CAT#20_3m', PandasSelect('COM_CAT#20_3m', fillna_zero=True)),
        ('COM_CAT#21_3m', PandasSelect('COM_CAT#21_3m', fillna_zero=True)),
        # ('COM_CAT#22_3m', PandasSelect('COM_CAT#22_3m', fillna_zero=True)),
        ('COM_CAT#23_3m', PandasSelect('COM_CAT#23_3m', fillna_zero=True)),
        # ('COM_CAT#27_3m', PandasSelect('COM_CAT#27_3m', fillna_zero=True)),
        ('COM_CAT#28_3m', PandasSelect('COM_CAT#28_3m', fillna_zero=True)),
        # ('COM_CAT#29_3m', PandasSelect('COM_CAT#29_3m', fillna_zero=True)),
        ('COM_CAT#30_3m', PandasSelect('COM_CAT#30_3m', fillna_zero=True)),
        ('COM_CAT#31_3m', PandasSelect('COM_CAT#31_3m', fillna_zero=True)),
        # ('COM_CAT#32_3m', PandasSelect('COM_CAT#32_3m', fillna_zero=True)),
        # ('COM_CAT#33_3m', PandasSelect('COM_CAT#33_3m', fillna_zero=True)),

        ('REVENUE_6m', PandasSelect('REVENUE_6m', fillna_zero=True)),
        # ('ITC_6m', PandasSelect('ITC_6m', fillna_zero=True)),
        ('VAS_6m', PandasSelect('VAS_6m', fillna_zero=True)),
        ('RENT_CHANNEL_6m', PandasSelect('RENT_CHANNEL_6m', fillna_zero=True)),
        ('ROAM_6m', PandasSelect('ROAM_6m', fillna_zero=True)),
        ('COST_6m', PandasSelect('COST_6m', fillna_zero=True)),
        ('COM_CAT#17_6m', PandasSelect('COM_CAT#17_6m', fillna_zero=True)),
        ('COM_CAT#18_6m', PandasSelect('COM_CAT#18_6m', fillna_zero=True)),
        ('COM_CAT#19_6m', PandasSelect('COM_CAT#19_6m', fillna_zero=True)),
        ('COM_CAT#20_6m', PandasSelect('COM_CAT#20_6m', fillna_zero=True)),
        ('COM_CAT#21_6m', PandasSelect('COM_CAT#21_6m', fillna_zero=True)),
        # ('COM_CAT#22_6m', PandasSelect('COM_CAT#22_6m', fillna_zero=True)),
        # ('COM_CAT#23_6m', PandasSelect('COM_CAT#23_6m', fillna_zero=True)),
        # ('COM_CAT#27_6m', PandasSelect('COM_CAT#27_6m', fillna_zero=True)),
        # ('COM_CAT#28_6m', PandasSelect('COM_CAT#28_6m', fillna_zero=True)),
        ('COM_CAT#29_6m', PandasSelect('COM_CAT#29_6m', fillna_zero=True)),
        ('COM_CAT#30_6m', PandasSelect('COM_CAT#30_6m', fillna_zero=True)),
        ('COM_CAT#31_6m', PandasSelect('COM_CAT#31_6m', fillna_zero=True)),
        ('COM_CAT#32_6m', PandasSelect('COM_CAT#32_6m', fillna_zero=True)),
        # ('COM_CAT#33_6m', PandasSelect('COM_CAT#33_6m', fillna_zero=True)),

        ('REVENUE_diff_1m', PandasSelect('REVENUE_diff_1m', fillna_zero=True)),
        ('ITC_diff_1m', PandasSelect('ITC_diff_1m', fillna_zero=True)),
        ('VAS_diff_1m', PandasSelect('VAS_diff_1m', fillna_zero=True)),
        ('RENT_CHANNEL_diff_1m', PandasSelect('RENT_CHANNEL_diff_1m', fillna_zero=True)),
        ('ROAM_diff_1m', PandasSelect('ROAM_diff_1m', fillna_zero=True)),
        ('COST_diff_1m', PandasSelect('COST_diff_1m', fillna_zero=True)),
        ('COM_CAT#17_diff_1m', PandasSelect('COM_CAT#17_diff_1m', fillna_zero=True)),
        # ('COM_CAT#18_diff_1m', PandasSelect('COM_CAT#18_diff_1m', fillna_zero=True)),
        ('COM_CAT#19_diff_1m', PandasSelect('COM_CAT#19_diff_1m', fillna_zero=True)),
        ('COM_CAT#20_diff_1m', PandasSelect('COM_CAT#20_diff_1m', fillna_zero=True)),
        ('COM_CAT#21_diff_1m', PandasSelect('COM_CAT#21_diff_1m', fillna_zero=True)),
        ('COM_CAT#22_diff_1m', PandasSelect('COM_CAT#22_diff_1m', fillna_zero=True)),
        ('COM_CAT#23_diff_1m', PandasSelect('COM_CAT#23_diff_1m', fillna_zero=True)),
        ('COM_CAT#27_diff_1m', PandasSelect('COM_CAT#27_diff_1m', fillna_zero=True)),
        # ('COM_CAT#28_diff_1m', PandasSelect('COM_CAT#28_diff_1m', fillna_zero=True)),
        ('COM_CAT#29_diff_1m', PandasSelect('COM_CAT#29_diff_1m', fillna_zero=True)),
        ('COM_CAT#30_diff_1m', PandasSelect('COM_CAT#30_diff_1m', fillna_zero=True)),
        ('COM_CAT#31_diff_1m', PandasSelect('COM_CAT#31_diff_1m', fillna_zero=True)),
        ('COM_CAT#32_diff_1m', PandasSelect('COM_CAT#32_diff_1m', fillna_zero=True)),
        ('COM_CAT#33_diff_1m', PandasSelect('COM_CAT#33_diff_1m', fillna_zero=True)),

        ('REVENUE_diff_2m', PandasSelect('REVENUE_diff_2m', fillna_zero=True)),
        # ('ITC_diff_2m', PandasSelect('ITC_diff_2m', fillna_zero=True)),
        ('VAS_diff_2m', PandasSelect('VAS_diff_2m', fillna_zero=True)),
        ('RENT_CHANNEL_diff_2m', PandasSelect('RENT_CHANNEL_diff_2m', fillna_zero=True)),
        # ('ROAM_diff_2m', PandasSelect('ROAM_diff_2m', fillna_zero=True)),
        ('COST_diff_2m', PandasSelect('COST_diff_2m', fillna_zero=True)),
        ('COM_CAT#17_diff_2m', PandasSelect('COM_CAT#17_diff_2m', fillna_zero=True)),
        ('COM_CAT#18_diff_2m', PandasSelect('COM_CAT#18_diff_2m', fillna_zero=True)),
        # ('COM_CAT#19_diff_2m', PandasSelect('COM_CAT#19_diff_2m', fillna_zero=True)),
        # ('COM_CAT#20_diff_2m', PandasSelect('COM_CAT#20_diff_2m', fillna_zero=True)),
        # ('COM_CAT#21_diff_2m', PandasSelect('COM_CAT#21_diff_2m', fillna_zero=True)),
        ('COM_CAT#22_diff_2m', PandasSelect('COM_CAT#22_diff_2m', fillna_zero=True)),
        ('COM_CAT#23_diff_2m', PandasSelect('COM_CAT#23_diff_2m', fillna_zero=True)),
        # ('COM_CAT#27_diff_2m', PandasSelect('COM_CAT#27_diff_2m', fillna_zero=True)),
        # ('COM_CAT#28_diff_2m', PandasSelect('COM_CAT#28_diff_2m', fillna_zero=True)),
        ('COM_CAT#29_diff_2m', PandasSelect('COM_CAT#29_diff_2m', fillna_zero=True)),
        # ('COM_CAT#30_diff_2m', PandasSelect('COM_CAT#30_diff_2m', fillna_zero=True)),
        # ('COM_CAT#31_diff_2m', PandasSelect('COM_CAT#31_diff_2m', fillna_zero=True)),
        ('COM_CAT#32_diff_2m', PandasSelect('COM_CAT#32_diff_2m', fillna_zero=True)),
        ('COM_CAT#33_diff_2m', PandasSelect('COM_CAT#33_diff_2m', fillna_zero=True)),

        ('REVENUE_diff_3m', PandasSelect('REVENUE_diff_3m', fillna_zero=True)),
        # ('ITC_diff_3m', PandasSelect('ITC_diff_3m', fillna_zero=True)),
        ('VAS_diff_3m', PandasSelect('VAS_diff_3m', fillna_zero=True)),
        ('RENT_CHANNEL_diff_3m', PandasSelect('RENT_CHANNEL_diff_3m', fillna_zero=True)),
        ('ROAM_diff_3m', PandasSelect('ROAM_diff_3m', fillna_zero=True)),
        ('COST_diff_3m', PandasSelect('COST_diff_3m', fillna_zero=True)),
        ('COM_CAT#17_diff_3m', PandasSelect('COM_CAT#17_diff_3m', fillna_zero=True)),
        # ('COM_CAT#18_diff_3m', PandasSelect('COM_CAT#18_diff_3m', fillna_zero=True)),
        ('COM_CAT#19_diff_3m', PandasSelect('COM_CAT#19_diff_3m', fillna_zero=True)),
        # ('COM_CAT#20_diff_3m', PandasSelect('COM_CAT#20_diff_3m', fillna_zero=True)),
        ('COM_CAT#21_diff_3m', PandasSelect('COM_CAT#21_diff_3m', fillna_zero=True)),
        ('COM_CAT#22_diff_3m', PandasSelect('COM_CAT#22_diff_3m', fillna_zero=True)),
        ('COM_CAT#23_diff_3m', PandasSelect('COM_CAT#23_diff_3m', fillna_zero=True)),
        # ('COM_CAT#27_diff_3m', PandasSelect('COM_CAT#27_diff_3m', fillna_zero=True)),
        # ('COM_CAT#28_diff_3m', PandasSelect('COM_CAT#28_diff_3m', fillna_zero=True)),
        # ('COM_CAT#29_diff_3m', PandasSelect('COM_CAT#29_diff_3m', fillna_zero=True)),
        # ('COM_CAT#30_diff_3m', PandasSelect('COM_CAT#30_diff_3m', fillna_zero=True)),
        # ('COM_CAT#31_diff_3m', PandasSelect('COM_CAT#31_diff_3m', fillna_zero=True)),
        ('COM_CAT#32_diff_3m', PandasSelect('COM_CAT#32_diff_3m', fillna_zero=True)),
        ('COM_CAT#33_diff_3m', PandasSelect('COM_CAT#33_diff_3m', fillna_zero=True)),

    ])),
    ('estimator', LogisticRegression(random_state=42,
                                     penalty='l2',
                                     C=0.1,
                                     class_weight='balanced',
                                     solver='liblinear',
                                     max_iter=200,
                                     n_jobs=1)),
    # ('estimator', SVC(gamma='auto', kernel='rbf', random_state=42, class_weight='balanced')),
    # ('estimator', ComplementNB()),
    # ('estimator', RandomForestClassifier(n_estimators=100, n_jobs=4))

])


def status_print(optim_result):
    """Status callback during bayesian hyperparameter search"""
    all_models = pd.DataFrame(bayes_cv_tuner.cv_results_)

    best_params = pd.Series(bayes_cv_tuner.best_params_)
    print(f'Best ROC-AUC: {np.round(bayes_cv_tuner.best_score_, 4),}, '
          f'current={np.round(bayes_cv_tuner.cv_results_["mean_test_score"][-1], 4)}, '
          f'std={np.round(bayes_cv_tuner.cv_results_["std_test_score"][-1], 4)}')
    # print('Model #{}\nBest ROC-AUC: {}\nBest params: {}\n'.format(
    #     len(all_models),
    #     np.round(bayes_cv_tuner.best_score_, 4),
    #     bayes_cv_tuner.best_params_
    # ))

    # Save all model results
    # if len(all_models)%10 == 0:
    #     clf_name = bayes_cv_tuner.estimator.named_steps['estimator'].__class__.__name__
    #     all_models.to_csv(f"cv_results/{clf_name}_cv_{datetime.now().strftime('%d_%H_%M')}.csv")


if __name__ == '__main__':
    train_df = load_csi_train()
    train_feat_df = load_features('train')

    train_df = merge_features(train_df, train_feat_df)
    train_df = add_weekday(train_df, 'CONTACT_DATE')
    train_df = add_holidays(train_df, 'CONTACT_DATE')
    train_y = train_df['CSI']
    train_X = train_df.drop(['CSI', 'CONTACT_DATE', 'SNAP_DATE'], axis=1)
    gc.collect()


    class FeaturePredictor(BaseEstimator):
        def __init__(self, **params):
            self.pipeline = Pipeline([
                ('subset', PandasSubset(**{k: True for k in features})),
                ('lgb', LGBMClassifier(objective='binary',
                                       learning_rate=0.2,
                                       num_leaves=7,
                                       max_depth=-1,
                                       min_child_samples=100,
                                       max_bin=105,
                                       subsample=0.7,
                                       subsample_freq=1,
                                       colsample_bytree=0.8,
                                       min_child_weight=0,
                                       subsample_for_bin=200000,
                                       min_split_gain=0,
                                       reg_alpha=0,
                                       reg_lambda=0,
                                       n_estimators=500,
                                       n_jobs=4,
                                       is_unbalance=True,
                                       random_state=42,
                                       class_weight='balanced'
                                       )),
            ])
            self.set_params(**params)

        def fit(self, X, y, **fit_params):
            Xs = self.pipeline.named_steps['subset'].fit_transform(train_X.loc[X])

            feats = self.pipeline.named_steps['subset'].fields()
            cats = list(set(categorical).intersection(feats))
            Xs_eval = self.pipeline.named_steps['subset'].transform(train_X.loc[train_X.index.difference(X)])
            y_eval = train_y.loc[train_X.index.difference(X)]
            self.pipeline.named_steps['lgb'].fit(Xs, y,
                                                 eval_metric="auc",
                                                 eval_set=(Xs_eval, y_eval),
                                                 early_stopping_rounds=100,
                                                 verbose=1,
                                                 feature_name=feats,
                                                 categorical_feature=cats,
                                                 )
            del Xs, y, Xs_eval, y_eval, feats, cats
            gc.collect()
            return self

        def predict(self, X):
            Xs = self.pipeline.named_steps['subset'].transform(train_X.loc[X])
            return self.pipeline.named_steps['lgb'].predict_proba(Xs)[:, 1]

        def predict_proba(self, X):
            Xs = self.pipeline.named_steps['subset'].transform(train_X.loc[X])
            return self.pipeline.named_steps['lgb'].predict_proba(Xs)

        def get_params(self, deep=True):
            return self.pipeline.get_params(deep)

        def set_params(self, **params):
            self.pipeline.set_params(**params)
            return self


    print("Training...")

    from time import time
    bayes_cv_tuner = BayesSearchCV(
        estimator=ppl,
        search_spaces=search_spaces,
        scoring='roc_auc',
        cv=RepeatedStratifiedKFold(4, 10, random_state=42),
        n_jobs=2,
        pre_dispatch=4,
        n_iter=100,
        verbose=0,
        refit=True,
        # random_state=42,
    )

    timer = time()
    result = bayes_cv_tuner.fit(train_X, train_y, callback=status_print)
    print(time()-timer)

    clf_name = bayes_cv_tuner.estimator.named_steps['estimator'].__class__.__name__
    all_models = pd.DataFrame(bayes_cv_tuner.cv_results_)
    all_models.to_csv(f"cv_results/{clf_name}_cv_{datetime.now().strftime('%d_%H_%M')}.csv")

    test_df = load_csi_test()
    test_feat_df = load_features('test')

    test_df = merge_features(test_df, test_feat_df)
    test_df = add_weekday(test_df, 'CONTACT_DATE')
    test_df = add_holidays(test_df, 'CONTACT_DATE')
    test_X = test_df.drop(['CONTACT_DATE', 'SNAP_DATE'], axis=1)

    adv_train_x, adv_train_y, adv_test_x, adv_test_y = adversial_train_test_split(train_X, train_y, test_X, topK=1000)
    bayes_cv_tuner._fit_best_model(adv_train_x, adv_train_y)
    adv_pred_y = bayes_cv_tuner.predict_proba(adv_test_x)[:, 1]
    adv_auc = roc_auc_score(adv_test_y, adv_pred_y)
    print(f'Adversial AUC = {adv_auc} by {len(adv_test_y)} samples')

    bayes_cv_tuner._fit_best_model(train_X, train_y)
    test_y = bayes_cv_tuner.predict_proba(test_X)
    df = pd.DataFrame(test_y[:, 1])
    df.to_csv(f"submits/"
              f"{bayes_cv_tuner.estimator.named_steps['estimator'].__class__.__name__}"
              f"_{datetime.now().strftime('%d_%H_%M')}"
              f"_{bayes_cv_tuner.best_score_:0.4f}"
              f"_{adv_auc:0.4f}.csv",
              header=None,
              index=None)


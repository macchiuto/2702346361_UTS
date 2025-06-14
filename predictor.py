# -*- coding: utf-8 -*-
"""predictor.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1QoTmPYPSwivn6b8dHopiC0FKKpuP_9Ad
"""

import pandas as pd
import pickle
from sklearn.preprocessing import OrdinalEncoder, LabelEncoder, OneHotEncoder

with open('tuned_xgb_model.pkl', 'rb') as f:
    model = pickle.load(f)

with open('ordinal_enc.pkl', 'rb') as f:
    ordinal_encoder = pickle.load(f)

with open('gender_enc.pkl', 'rb') as f:
    gender_encoder = pickle.load(f)

with open('default_enc.pkl', 'rb') as f:
    default_encoder = pickle.load(f)

with open('onehot_enc.pkl', 'rb') as f:
    onehot_encoder = pickle.load(f)

with open('final_columns.pkl', 'rb') as f:
    columns = pickle.load(f)

class LoanStatusPredictor:
    def __init__(self, model, ordinal_encoder, gender_encoder, default_encoder, onehot_encoder, columns):
        self.model = model
        self.ordinal_enc = ordinal_encoder
        self.gender_enc = gender_encoder
        self.default_enc = default_encoder
        self.onehot_enc = onehot_encoder
        self.columns = columns
        self.cat_cols = ['loan_intent', 'person_home_ownership']


    def preprocess(self, df):
        df = df.copy()

        df['person_gender'] = df['person_gender'].replace({'Male': 'male', 'fe male': 'female'})
        df['person_income'] = df['person_income'].fillna(df['person_income'].median())

        df['person_education'] = self.ordinal_enc.transform(df[['person_education']]) + 1
        df['person_gender'] = self.gender_enc.transform(df['person_gender'])
        df['previous_loan_defaults_on_file'] = self.default_enc.transform(df['previous_loan_defaults_on_file'])

        onehot_df = pd.DataFrame(
            self.onehot_enc.transform(df[self.cat_cols]),
            columns=self.onehot_enc.get_feature_names_out(self.cat_cols)
        )
        df = pd.concat([df.drop(self.cat_cols, axis=1).reset_index(drop=True), onehot_df], axis=1)

        df = df.reindex(columns=self.columns, fill_value=0)
        return df

    def predict(self, raw_df):
        X = self.preprocess(raw_df)
        return self.model.predict(X)

predictor = LoanStatusPredictor(model, ordinal_encoder, gender_encoder, default_encoder, onehot_encoder, columns)
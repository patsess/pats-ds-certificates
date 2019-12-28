
from pathlib import Path
import pandas as pd

__author__ = 'psessford'


SIMPLIFICATION_TUPLES = [
    ('nlp', 'natural language processing'),
    ('NLP', 'Natural Language Processing'),
    ('amazon web services', 'aws'),
    ('Amazon Web Services', 'AWS'),
    ('keras 2.0', 'keras'),
    ('Keras 2.0', 'Keras'),
]


MULTIWORD_TUPLES = [
    ('data science', 'datascience'),
    ('machine learning', 'machinelearning'),
    ('deep learning', 'deeplearning'),
    ('time series', 'timeseries'),
    ('big data', 'bigdata'),
    ('parallel computing', 'parallelcomputing'),
    ('parallel processing', 'parallelcomputing'),
    ('natural language processing', 'naturallanguageprocessing'),
    ('feature engineering', 'featureengineering'),
    ('software engineering', 'softwareengineering'),
]


def read_certificates_data():
    """Read in data on certificates using pandas

    :return carts_df: (pd.DataFrame)
    """
    module_path = str(Path(__file__).absolute().parent.parent)
    carts_df = pd.read_csv(
        module_path + '/certificates_info.txt', sep='|', header=0)
    return carts_df


if __name__ == '__main__':
    df = read_certificates_data()
    print(df.iloc[0])

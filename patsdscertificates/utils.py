
import os
import logging
from pathlib import Path
import pandas as pd
import glob
import ghostscript
import locale

__author__ = 'psessford'

logging.basicConfig(level=logging.INFO)


MODULE_PATH = str(Path(__file__).absolute().parent.parent)


SIMPLIFICATION_TUPLES = [
    ('natural language processing', 'NLP'),
    ('Natural Language Processing', 'NLP'),
    ('amazon web services', 'AWS'),
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
    carts_df = pd.read_csv(
        MODULE_PATH + '/certificates_info.txt', sep='|', header=0, index_col=0)
    return carts_df


def pdf2jpeg(pdf_input_path, jpeg_output_path):
    """Convert a pdf file to a jpeg

    Note: code taken from
    https://www.activestate.com/blog/using-python-to-convert-pdfs-to-images/.

    :param pdf_input_path: (str)
    :param jpeg_output_path: (str)
    """
    args = ["pef2jpeg",  # actual value doesn't matter
            "-dNOPAUSE",
            "-sDEVICE=jpeg",
            "-r144",
            "-sOutputFile=" + jpeg_output_path,
            pdf_input_path]

    encoding = locale.getpreferredencoding()
    args = [a.encode(encoding) for a in args]

    ghostscript.Ghostscript(*args)


def convert_certificates_to_jpegs():
    """Coverts any pdf certificates to jpeg files
    """
    pdf_files = glob.glob(MODULE_PATH + '/static/datacamp_certificates/*.pdf')
    # TODO: use Path instead of slashes above
    for pdf_file in pdf_files:
        logging.info('converting {} to jpeg'.format(pdf_file))
        pdf2jpeg(pdf_input_path=pdf_file,
                 jpeg_output_path=pdf_file.replace('.pdf', '.jpeg'))
        os.remove(pdf_file)


if __name__ == '__main__':
    convert_certificates_to_jpegs()
    df = read_certificates_data()
    print(df.iloc[0])

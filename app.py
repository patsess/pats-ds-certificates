
import sys
from pathlib import Path
module_path = str(Path(__file__).absolute().parent)
if module_path not in sys.path:
    sys.path.append(module_path)  # e.g. '.../repos/<name_of_this_repo>'

import logging
from flask import Flask, render_template
from patsdscertificates.utils import read_certificates_data

__author__ = 'psessford'

logging.basicConfig(level=logging.INFO)

"""
note: for details on deploying using Heroku, see 
https://stackabuse.com/deploying-a-flask-application-to-heroku/
"""


app = Flask(__name__)


@app.route("/")
def load_page():
    path_certs_wordcloud = '/static/images/certs_wordcloud.png'
    certs_df = read_certificates_data()
    course_titles_list = certs_df['title'].values.tolist()
    return render_template(
        'datacamp.html',
        path_certs_wordcloud=path_certs_wordcloud,
        course_titles_list=course_titles_list)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)

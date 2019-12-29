
import sys
from pathlib import Path
module_path = str(Path(__file__).absolute().parent)
if module_path not in sys.path:
    sys.path.append(module_path)  # e.g. '.../repos/<name_of_this_repo>'

import logging
from flask import Flask, render_template, url_for
from patsdscertificates.utils import read_certificates_data

__author__ = 'psessford'

logging.basicConfig(level=logging.INFO)

"""
note: for details on deploying using Heroku, see 
https://stackabuse.com/deploying-a-flask-application-to-heroku/
"""


app = Flask(__name__)


@app.route("/")
def main_page():
    """Load main page

    :return: **a rendered Flask template**
    """
    path_certs_wordcloud = '/static/images/certs_wordcloud.png'
    # TODO: use Path (and in course_page())
    certs_df = read_certificates_data()

    courses_list = _get_courses_list(certs_df=certs_df)
    wordcloud_description = _get_wordcloud_description()
    web_app_description = _get_web_app_description()

    return render_template(
        'datacamp.html',
        path_certs_wordcloud=path_certs_wordcloud,
        wordcloud_description=wordcloud_description,
        web_app_description=web_app_description,
        courses_list=courses_list)


@app.route("/course/<course_id>/")
def course_page(course_id):
    """Load page with information on an individual course

    :param course_id: (int) can also be a str that can be coerced into an int
    :return: **a rendered Flask template**
    """
    certs_df = read_certificates_data()
    # TODO: pass all required data over instead of reading it again?
    course_dict = certs_df.loc[int(course_id), :].to_dict()
    path_certificate = ('/static/datacamp_certificates/{}.jpeg'
                        .format(course_dict['certificate_id']))
    return render_template(
        'course_page.html',
        course_id=course_id,
        course_title=course_dict['title'],
        course_description=course_dict['description'],
        path_certificate=path_certificate)


def _get_courses_list(certs_df):
    course_titles_dict = certs_df['title'].to_dict()
    course_titles_list = [
        _get_course_title_html(course_id=id_, course_title=title_)
        for id_, title_ in course_titles_dict.items()]
    courses_list = certs_df['month'].str.cat(
        course_titles_list, sep=' - ').values.tolist()
    return courses_list


def _get_course_title_html(course_id, course_title):
    course_page_url = url_for('course_page', course_id=course_id)
    course_title_html = (
        f'<a href="{course_page_url}"><span class="course_title">'
        f'{course_title}</span></a>')
    print(course_title_html)
    return course_title_html


def _get_wordcloud_description():
    with open('static/texts/wordcloud_description.txt', 'r') as f:
        wordcloud_description = f.read()

    github_url = ('https://github.com/patsess/pats-ds-certificates/blob/'
                  'master/patsdscertificates/certs_wordcloud.py')
    wordcloud_description = _add_link_to_text(
        text=wordcloud_description, href_str='GitHub', url=github_url)
    return wordcloud_description


def _add_link_to_text(text, href_str, url):
    text = text.replace(
        href_str, '<a href="{}">{}</a>'.format(url, href_str))
    return text


def _get_web_app_description():
    with open('static/texts/web_app_description.txt', 'r') as f:
        web_app_description = f.read()

    # flask_url = 'flask.palletsprojects.com'
    flask_url = 'https://en.wikipedia.org/wiki/Flask_(web_framework)'
    web_app_description = _add_link_to_text(
        text=web_app_description, href_str='Flask', url=flask_url)

    heroku_url = 'https://www.heroku.com'
    web_app_description = _add_link_to_text(
        text=web_app_description, href_str='Heroku', url=heroku_url)

    github_url = 'https://github.com/patsess/pats-ds-certificates'
    web_app_description = _add_link_to_text(
        text=web_app_description, href_str='GitHub', url=github_url)
    return web_app_description


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)

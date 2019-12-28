
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
# from PIL import Image
import spacy
from wordcloud import WordCloud, STOPWORDS#, ImageColorGenerator
from patsdscertificates.utils import SIMPLIFICATION_TUPLES, MULTIWORD_TUPLES

__author__ = 'psessford'


class CertificatesWordCloud(object):
    # TODO: docstr
    def __init__(self, certs_df):
        # TODO: docstr
        self.certs_df = certs_df

    def get_text_string(self, data_source='title'):
        # TODO: docstr
        if data_source not in self.certs_df.columns.values:
            raise ValueError('data_source must be a column of carts_df ({} '
                             'provided)'.format(data_source))

        text = ' '.join(d for d in self.certs_df[data_source].values)
        text = text.replace('\n', ' ').replace('\r', '').strip()
        return text

    def generate_certificate_wordcloud(self, text, method='simple',
                                       show_plot=True, write_plot=False):
        """TODO: finished docstr

        :param text:
        :return:
        """
        for unwanted_, wanted_ in SIMPLIFICATION_TUPLES:# + MULTIWORD_TUPLES:
            text = text.replace(unwanted_, wanted_)

        nlp = CertificatesWordCloud._get_spacy_nlp(method=method)
        doc = nlp(text)
        words = CertificatesWordCloud._get_words_list(doc=doc, method=method)

        for wanted_word, unwanted_word in MULTIWORD_TUPLES:
            words = [wanted_word if w == unwanted_word else w for w in words]

        # wordcloud = WordCloud(
        #     stopwords=stopwords, background_color='white').generate(text)

        frequencies = pd.Series(words).value_counts().to_dict()
        wordcloud = WordCloud(background_color='white', random_state=0)
        wordcloud.generate_from_frequencies(frequencies)

        if show_plot:
            CertificatesWordCloud._plot_wordcloud(wordcloud=wordcloud)

        if write_plot:
            wordcloud.to_file(CertificatesWordCloud.get_path_to_wordcloud())

    @staticmethod
    def get_path_to_wordcloud():
        module_path = str(Path(__file__).absolute().parent.parent)
        path_to_wordcloud = (
            module_path + '/static/images/certs_wordcloud.png')
        # TODO: update to use cross-platform Path
        return path_to_wordcloud

    @staticmethod
    def _get_spacy_nlp(method):
        if method == 'simple':
            nlp = spacy.load('en_core_web_sm')
        elif method == 'use_entities':
            nlp = spacy.load('en_core_web_lg')
        else:
            raise ValueError('unrecognised method ({})'.format(method))

        return nlp

    @staticmethod
    def _get_words_list(doc, method):
        if method == 'simple':
            stopwords = set(STOPWORDS)
            stopwords.update(
                ['advanced', 'fundamentals', 'intermediate', 'intro',
                 'introduction'])
            words = [token.lemma_ for token in doc
                     if ((not token.is_punct) and token.text not in stopwords)]
        elif method == 'use_entities':
            words = [ent.lemma_ for ent in doc.ents
                     if ent.label_ not in ['DATE', 'CARDINAL']]
        else:
            raise ValueError('unrecognised method ({})'.format(method))

        return words

    @staticmethod
    def _plot_wordcloud(wordcloud):
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.show()


if __name__ == '__main__':
    from patsdscertificates.utils import read_certificates_data
    certs_df = read_certificates_data()
    wc = CertificatesWordCloud(certs_df=certs_df)
    text = wc.get_text_string(data_source='description')
    wc.generate_certificate_wordcloud(
        text=text, method='use_entities', write_plot=False)

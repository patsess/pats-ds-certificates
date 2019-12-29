
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
# from PIL import Image
import spacy
from wordcloud import WordCloud, STOPWORDS#, ImageColorGenerator
from patsdscertificates.utils import SIMPLIFICATION_TUPLES, MULTIWORD_TUPLES

__author__ = 'psessford'

# TODO: add logging
# TODO: add classmethod?
# TODO: add course descriptions to web app, using hyperlinks to separate pages
# TODO: add to CV, and consider emailing it Markus and Chi (but maybe after I've updated more?)


class CertificatesWordCloud(object):
    # TODO: docstr
    def __init__(self, certs_df):
        # TODO: docstr
        self.certs_df = certs_df

        self.nlp_models = {}  # initialise

    def get_text_strings(self, data_source='title'):
        # TODO: docstr
        if data_source not in self.certs_df.columns.values:
            raise ValueError('data_source must be a column of carts_df ({} '
                             'provided)'.format(data_source))

        data_source_series = (
            self.certs_df[data_source] if data_source == 'title'
            else self.certs_df['title'].str.cat(
                self.certs_df[data_source], sep=': '))

        # text = ' '.join(d for d in data_source_series.values)
        # text = text.replace('\n', ' ').replace('\r', '').strip()
        texts = [t.replace('\n', ' ').replace('\r', '').strip()
                 for t in data_source_series.values]
        return texts

    def get_words_from_texts(self, texts, method='simple'):
        """TODO: finished docstr: note: a spacy model will take the tokens of the text in context, so each text should be processed separately by spacy

        :param texts:
        :return:
        """
        words = [
            self._get_words_from_single_text(
                text=text, method=method) for text in texts]
        words = [item for sublist in words for item in sublist]
        return words

    def generate_certificate_wordcloud(self, words, show_plot=True,
                                       write_plot=False):
        # TODO: docstr
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

    def _get_words_from_single_text(self, text, method='simple'):
        for unwanted_, wanted_ in SIMPLIFICATION_TUPLES:# + MULTIWORD_TUPLES:
            text = text.replace(unwanted_, wanted_)

        nlp = self._get_spacy_nlp(method=method)
        doc = nlp(text)
        words = CertificatesWordCloud._get_words_list(doc=doc, method=method)

        for wanted_word, unwanted_word in MULTIWORD_TUPLES:
            words = [wanted_word if w == unwanted_word else w for w in words]

        return words

    def _get_spacy_nlp(self, method):
        if method == 'simple':
            model_name = 'en_core_web_sm'
        elif method == 'use_entities':
            # model_name = 'en_core_web_lg'
            model_name = 'en_core_web_md'
        else:
            raise ValueError('unrecognised method ({})'.format(method))

        self.nlp_models[method] = self.nlp_models.get(
            method, spacy.load(model_name))
        return self.nlp_models[method]

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
    texts = wc.get_text_strings(data_source='description')
    words = wc.get_words_from_texts(texts=texts, method='use_entities')
    wc.generate_certificate_wordcloud(words=words, write_plot=True)

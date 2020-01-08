
import logging
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import spacy
from wordcloud import WordCloud, STOPWORDS
from patsdscertificates.utils import SIMPLIFICATION_TUPLES, MULTIWORD_TUPLES

__author__ = 'psessford'


class CertificatesWordCloud(object):
    """Helper to generate a wordcloud for certificates
    """
    @classmethod
    def generate_wordcloud_from_data(cls, data_source='description',
                                     method='use_entities', show_plot=True,
                                     write_plot=False):
        """Generate a wordcloud

        :param data_source: (str) see cls.get_text_strings()
        :param method: (str) see cls.get_words_from_texts()
        :param show_plot: (bool) see cls.generate_wordcloud_from_words()
        :param write_plot: (bool) see cls.generate_wordcloud_from_words()
        """
        from patsdscertificates.utils import read_certificates_data
        certs_df = read_certificates_data()
        wc = cls(certs_df=certs_df)
        texts = wc.get_text_strings(data_source=data_source)
        words = wc.get_words_from_texts(texts=texts, method=method)
        wc.generate_wordcloud_from_words(
            words=words, show_plot=show_plot, write_plot=write_plot)

    def __init__(self, certs_df):
        """
        :param certs_df: (pd.DataFrame) information on certificates
        """
        self.certs_df = certs_df

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.logger.info('initialising a {} instance'
                         .format(self.__class__.__name__))

        # initialise useful attributes
        self.nlp_models = {}

    def get_text_strings(self, data_source='title'):
        """Get strings of text for a wordcloud

        :param data_source: (str) key word to indicate which data to get the
            texts from (e.g. course titles or course descriptions)
        :return texts: (list of str)
        """
        self.logger.info('getting text strings from data source {}'
                         .format(data_source))

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
        """Get individual words (or phrases) from fuller texts

        Note: a spacy model will take the tokens of the text in context, so
        each text should be processed separately by spacy.

        :param texts: (list of str) texts for a wordcloud
        :param method: (str) key word to indicate the method for the
            extraction of the words (or phrases)
        :return words: (list of str) individual words (or phrases) for a
            wordcloud
        """
        self.logger.info('getting words from text strings using method {}'
                         .format(method))
        words = [
            self._get_words_from_single_text(
                text=text, method=method) for text in texts]
        words = [item for sublist in words for item in sublist]
        return words

    def generate_wordcloud_from_words(self, words, show_plot=True,
                                      write_plot=False):
        """Generate a wordcloud from a list of words (or phrases)

        :param words: (list of str) words (or phrases) for wordcloud
        :param show_plot: (bool) whether to show the wordcloud
        :param write_plot: (bool) whether to save the wordcloud
        """
        self.logger.info('generating certificate wordcloud (with show_plot '
                         '{}, write_plot {})'.format(show_plot, write_plot))

        # wordcloud = WordCloud(
        #     stopwords=stopwords, background_color='white').generate(text)

        frequencies = pd.Series(words).value_counts().to_dict()
        self.logger.info('word frequencies: {}'.format(frequencies))
        wordcloud = WordCloud(background_color='white', random_state=0)
        wordcloud.generate_from_frequencies(frequencies)

        if show_plot:
            self._plot_wordcloud(wordcloud=wordcloud)

        if write_plot:
            wordcloud_file_path = self.get_path_to_wordcloud()
            wordcloud.to_file(wordcloud_file_path)
            self.logger.info('written wordcloud to file {}'
                             .format(wordcloud_file_path))

    @staticmethod
    def get_path_to_wordcloud():
        module_path = str(Path(__file__).absolute().parent.parent)
        path_to_wordcloud = (
            Path(module_path + '/static/images/') / 'certs_wordcloud.png')
        return path_to_wordcloud

    def _get_words_from_single_text(self, text, method='simple'):
        for unwanted_, wanted_ in SIMPLIFICATION_TUPLES:# + MULTIWORD_TUPLES:
            text = text.replace(unwanted_, wanted_)

        nlp = self._get_spacy_nlp(method=method)
        doc = nlp(text)
        words = CertificatesWordCloud._get_words_list(doc=doc, method=method)

        for wanted_word, unwanted_word in MULTIWORD_TUPLES:
            words = [wanted_word if w == unwanted_word else w for w in words]

        self.logger.info('words from a single text: {}'.format(words))
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
    from patsdscertificates.utils import convert_certificates_to_jpegs
    convert_certificates_to_jpegs()
    CertificatesWordCloud.generate_wordcloud_from_data(
        data_source='description', method='use_entities', show_plot=True,
        write_plot=False)

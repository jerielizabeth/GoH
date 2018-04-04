import unittest
import GoH.corpora as corpora
from GoH.preprocess import ENTITIES
from nltk import word_tokenize


class PagePreprocessingCase(unittest.TestCase):

    def setUp(self):
        self.page = "A human system is full of moral obligations, but the true faith in God shineth down on the poor man."

    def test_process_page(self):
        self.assertEqual(corpora.process_page(self.page),
            "A human system is full of moral obligations  but the true faith in God shineth down on the poor man ",
            "The text was not properly processed"
            )

    def test_connect_phrases(self):
        self.assertEqual(corpora.connect_phrases(corpora.process_page(self.page), entities=ENTITIES),
            "a human_system is full of moral obligations  but the true_faith in god shineth down on the poor_man ",
            "Phrases are not properly connected"
            )

    def test_lemmatize_tokens(self):
        tokens = word_tokenize(corpora.connect_phrases(corpora.process_page(self.page), entities=ENTITIES))
        self.assertEqual(corpora.lemmatize_tokens(tokens),
            ["a","human_system", "is", "full", "of", "moral", "obligation", "but", "the", "true_faith", "in", "god", "shineth", "down", "on", "the", "poor_man"],
            "Error in the lemmatizing step"
            )

    def test_filter_tokens(self):
        self.assertEqual(corpora.filter_tokens(corpora.lemmatize_tokens(word_tokenize(corpora.connect_phrases(corpora.process_page(self.page), entities=ENTITIES)))),
            ["human_system", "moral", "obligation", "true_faith", "god", "shineth", "poor_man"],
             "Error in the filtering step"
            )

if __name__ == '__main__':
    unittest.main(verbosity=2)
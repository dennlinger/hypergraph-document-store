from unittest import TestCase


class TestTermGenerator(TestCase):
    # simply check whether the init function runs smoothly (not necessarily successfully, but gracefully)
    def test___init__(self):
        from TermGenerator import TermGenerator
        tg = TermGenerator(num_distinct_documents=0, log_file="test.log")

    def test___init___with_nonzero_distinct_documents(self):
        from TermGenerator import TermGenerator
        tg = TermGenerator(num_distinct_documents=5, log_file="test.log")

    def test___init___with_additional_stopwords(self):
        from TermGenerator import TermGenerator
        tg = TermGenerator(num_distinct_documents=1, log_file="test.log", custom_stopwords=["Obama"])

    def test_parse_results(self):
        from TermGenerator import TermGenerator
        tg = TermGenerator(num_distinct_documents=1, log_file="test.log", custom_stopwords=["Obama"])
        tg.parse()

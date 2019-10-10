from unittest import TestCase


class TestDocumentGenerator(TestCase):
    # simply check whether the init function runs smoothly (not necessarily successfully, but gracefully)
    def test___init__(self):
        from DocumentGenerator import DocumentGenerator
        dg = DocumentGenerator(num_distinct_documents=0, log_file="test.log")

    # test for non-zero limit
    def test___init___with_nonzero_distinct_documents(self):
        from DocumentGenerator import DocumentGenerator
        dg = DocumentGenerator(num_distinct_documents=5, log_file="test.log")

    def test__retrieve(self):
        from DocumentGenerator import DocumentGenerator
        dg = DocumentGenerator(num_distinct_documents=1, log_file="test.log")
        dg.retrieve()
        assert dg.data



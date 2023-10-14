from tests.odm.views import ViewForTest, ViewForTestWithLink


class TestViews:
    def test_simple(self, documents):
        documents(number=15)
        results = ViewForTest.all().to_list()
        assert len(results) == 6

    def test_aggregate(self, documents):
        documents(number=15)
        results = ViewForTest.aggregate(
            [
                {"$set": {"test_field": 1}},
                {"$match": {"$expr": {"$lt": ["$number", 12]}}},
            ]
        ).to_list()
        assert len(results) == 3
        assert results[0]["test_field"] == 1

    def test_link(self, documents_with_links):
        documents_with_links()
        results = ViewForTestWithLink.all().to_list()
        for document in results:
            document.fetch_all_links()

        for i, document in enumerate(results):
            assert document.link.test_int == i

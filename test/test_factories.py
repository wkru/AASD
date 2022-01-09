import unittest

from factories.reviewCollector import ReviewCollectorFactory
from config import DOMAIN


class TestFactories(unittest.TestCase):
    def setUp(self) -> None:
        self.factory = ReviewCollectorFactory()

    def test_generate_jid(self):
        jid = self.factory._generate_jid(0)
        template = ReviewCollectorFactory.jid_template
        cur_id = self.factory.cur_id
        self.assertEqual(jid, f'{template}-{cur_id}@{DOMAIN}')

    def test_agent_jid_changes(self):
        self.assertEqual(self.factory.cur_id, 0)
        self.factory.create_agent()
        self.assertEqual(self.factory.cur_id, 1)
        self.factory.create_agent()
        self.assertEqual(self.factory.cur_id, 2)


if __name__ == '__main__':
    unittest.main()

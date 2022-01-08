import unittest

from factories.reviewCollector import ReviewCollectorFactory
from config import DOMAIN


class TestFactories(unittest.TestCase):
    def test_generate_jid(self):
        jid = ReviewCollectorFactory._generate_jid(0)
        template = ReviewCollectorFactory.jid_template
        cur_id = ReviewCollectorFactory.cur_id
        self.assertEqual(jid, f'{template}-{cur_id}@{DOMAIN}')

    def test_agent_jid_changes(self):
        rc0 = ReviewCollectorFactory.create_agent()
        self.assertEqual(rc0.jid, ReviewCollectorFactory._generate_jid(0))

        rc1 = ReviewCollectorFactory.create_agent()
        self.assertEqual(rc1.jid, ReviewCollectorFactory._generate_jid(1))


if __name__ == '__main__':
    unittest.main()

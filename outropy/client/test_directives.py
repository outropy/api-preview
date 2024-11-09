from unittest import TestCase


class TestDirectives(TestCase):
    def test_directives_initialized(self) -> None:
        self.skipTest("TODO")
        # expectations = [{
        #     'session_id': 'a123',
        #     'latency': 1,
        #     'accuracy': 2,
        #     'cost': 10,
        #     'reproducibility': 20,
        #     'freshness': 30,
        #     'personalization': 44,
        #     'recall': 31
        # }, {
        #     'session_id': 'a123',
        #     'latency': BEST_EFFORT,
        #     'accuracy': 1,
        #     'cost': 10,
        #     'reproducibility': 20,
        #     'freshness': 31,
        #     'personalization': 44,
        #     'recall': 30
        # }]
        #
        # for expectation in expectations:
        #     directives = Directives(**expectation)
        #     self.assertEqual(directives.session_id, expectation['session_id'])
        #     self.assertEqual(directives.latency, expectation['latency'])
        #
        #     self.assertEqual(directives.cost, expectation['cost'])
        #     self.assertEqual(directives.reproducibility, expectation['reproducibility'])
        #     self.assertEqual(directives.freshness, expectation['freshness'])
        #     self.assertEqual(directives.personalization, expectation['personalization'])
        #     self.assertEqual(directives.recall, expectation['recall'])

    def test_reject_values_under_0_or_abov_100(self) -> None:
        self.skipTest("TODO")
        # out_of_range = [{
        #     'session_id': '123',
        #     'latency': -1,
        #     'quality': 1,
        #     'cost': 10,
        #     'reproducibility': 20,
        #     'freshness': 30,
        #     'personalization': 44,
        #     'recall': 31
        # }, {
        #     'session_id': '123',
        #     'latency': 101,
        #     'quality': 1,
        #     'cost': 10,
        #     'reproducibility': 20,
        #     'freshness': 30,
        #     'personalization': 44,
        #     'recall': 30
        # }]
        #
        # for out in out_of_range:
        #     with self.assertRaises(ValueError):
        #         Directives(**out)

    def test_reject_duplicated_weights(self) -> None:
        self.skipTest("TODO")
        # duplicated = [{
        #     'session_id': '123',
        #     'latency': 1,
        #     'accuracy': 1,
        #     'cost': 10,
        #     'reproducibility': 20,
        #     'freshness': 30,
        #     'personalization': 44,
        #     'recall': 31
        # }, {
        #     'session_id': '123',
        #     'latency': BEST_EFFORT,
        #     'accuracy': 1,
        #     'cost': 10,
        #     'reproducibility': 20,
        #     'freshness': 30,
        #     'personalization': 44,
        #     'recall': 30
        # }]
        #
        # for dupes in duplicated:
        #     with self.assertRaises(ValueError):
        #         Directives(**dupes)

    def test_reject_goes_above_100(self) -> None:
        self.skipTest("TODO")
        # above_100 = [{
        #     'session_id': '123',
        #     'latency': 100,
        #     'accuracy': 1,
        #     'cost': 2,
        #     'reproducibility': 3,
        #     'freshness': 4,
        #     'personalization': 5,
        #     'recall': 6
        # }, {
        #     'session_id': '123',
        #     'latency': 0,
        #     'accuracy': 1,
        #     'cost': 2,
        #     'reproducibility': 3,
        #     'freshness': 4,
        #     'personalization': 5,
        #     'recall': 101,
        #     'creativity': 100
        # }]
        #
        # for above in above_100:
        #     with self.assertRaises(ValueError):
        #         Directives(**above)

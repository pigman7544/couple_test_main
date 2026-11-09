"""Smoke checks for the reproducible 12-archetype audit."""
import unittest
from audit_quality import audit


class AuditQualityTests(unittest.TestCase):
    def test_repeated_complete_output_and_sample_distribution(self):
        result = audit(samples=120, repeat=5, seed=20261109)
        self.assertTrue(result['deterministic'])
        self.assertEqual(sum(result['counts'].values()), 120)
        self.assertEqual(len(result['quality']), 12)
        self.assertGreaterEqual(result['matched_types'], 1)


if __name__ == '__main__':
    unittest.main()

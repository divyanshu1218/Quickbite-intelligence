import unittest
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents.graph import run_agent_pipeline

class TestAgentFlow(unittest.TestCase):

    def test_q1_agent_flow(self):
        print("\nTesting Q1 Agent Flow Integration...")
        q = "What were the total revenue, orders and AOV for the last 3 months?"
        res = run_agent_pipeline(q)
        
        self.assertEqual(res["analysis_type"], "revenue_overview")
        self.assertEqual(res["verification"]["status"], "passed")
        self.assertGreater(res["metrics"]["revenue"], 0)
        self.assertGreater(res["metrics"]["orders"], 0)
        self.assertGreater(res["metrics"]["aov"], 0)
        self.assertGreater(len(res["evidence"]), 0)
        self.assertGreater(len(res["trace"]), 0)
        print("Q1 Flow Passed successfully.")

    def test_q8_agent_flow(self):
        print("\nTesting Q8 Agent Flow Integration...")
        q = "Which stores consistently declined in the last 3 months and why?"
        res = run_agent_pipeline(q)
        
        self.assertEqual(res["analysis_type"], "store_diagnostic")
        self.assertEqual(res["verification"]["status"], "passed")
        # Should have declining stores list
        self.assertIn("declining_stores", res["metrics"])
        self.assertGreater(len(res["metrics"]["declining_stores"]), 0)
        self.assertGreater(len(res["evidence"]), 0)
        self.assertGreater(len(res["trace"]), 0)
        print("Q8 Flow Passed successfully.")

    def test_unsupported_flow(self):
        print("\nTesting Unsupported Query Flow...")
        q = "Who is the Prime Minister of India?"
        res = run_agent_pipeline(q)
        self.assertEqual(res["analysis_type"], "unsupported")
        print("Unsupported flow handled correctly.")

if __name__ == "__main__":
    unittest.main()

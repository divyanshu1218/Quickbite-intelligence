import unittest
import os
import sys

# Ensure project root is in PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.tools.revenue import get_last_n_month_metrics
from backend.tools.stores import get_store_rankings, get_consistently_declining_stores
from backend.tools.channels import get_channel_performance
from backend.tools.products import get_top_skus
from backend.tools.cities import get_city_revenue_trend
from backend.tools.periods import compare_weekend_weekday, compare_festive_normal
from backend.tools.diagnostics import get_store_diagnostic_metrics

class TestAnalyticalTools(unittest.TestCase):

    def test_revenue_metrics(self):
        print("\nTesting Revenue Metrics (Q1)...")
        res = get_last_n_month_metrics(3)
        self.assertIn("revenue", res)
        self.assertIn("orders", res)
        self.assertIn("aov", res)
        self.assertIn("changes", res)
        self.assertIn("monthly_data", res)
        self.assertGreater(res["revenue"], 0)
        self.assertGreater(res["orders"], 0)
        self.assertGreater(res["aov"], 0)
        self.assertEqual(len(res["monthly_data"]), 3)
        print(f"Passed. Last 3 Months: Revenue={res['revenue']}, Orders={res['orders']}, AOV={res['aov']}")

    def test_store_rankings(self):
        print("\nTesting Store Rankings (Q2)...")
        res = get_store_rankings(top_n=5, bottom_n=5)
        self.assertIn("top_stores", res)
        self.assertIn("bottom_stores", res)
        self.assertIn("all_stores", res)
        self.assertEqual(len(res["top_stores"]), 5)
        self.assertEqual(len(res["bottom_stores"]), 5)
        # Check order sorting
        self.assertGreaterEqual(res["top_stores"][0]["revenue"], res["top_stores"][1]["revenue"])
        self.assertLessEqual(res["bottom_stores"][0]["revenue"], res["bottom_stores"][1]["revenue"])
        print("Passed.")

    def test_channel_analysis(self):
        print("\nTesting Channel Performance (Q3)...")
        res = get_channel_performance()
        self.assertIn("channels", res)
        self.assertIn("total_revenue", res)
        self.assertGreater(len(res["channels"]), 0)
        # Verify share sum is close to 100
        shares_sum = sum(c["share_pct"] for c in res["channels"])
        self.assertAlmostEqual(shares_sum, 100.0, places=1)
        print("Passed.")

    def test_top_skus(self):
        print("\nTesting Top SKUs (Q4)...")
        res = get_top_skus(top_n=5)
        self.assertIn("top_by_quantity", res)
        self.assertIn("top_by_revenue", res)
        self.assertEqual(len(res["top_by_quantity"]), 5)
        self.assertEqual(len(res["top_by_revenue"]), 5)
        self.assertGreater(res["top_by_quantity"][0]["quantity_sold"], 0)
        self.assertGreater(res["top_by_revenue"][0]["revenue"], 0)
        print("Passed.")

    def test_city_decline(self):
        print("\nTesting City Revenue Trends (Q5)...")
        res = get_city_revenue_trend()
        self.assertIn("declining_cities", res)
        self.assertIn("stable_growing_cities", res)
        # All declining cities should have overall negative change
        for city in res["declining_cities"]:
            self.assertLess(city["revenue_change"], 0)
        print("Passed.")

    def test_weekend_weekday(self):
        print("\nTesting Weekend vs Weekday Performance (Q6)...")
        res = compare_weekend_weekday()
        self.assertIn("Weekday", res)
        self.assertIn("Weekend", res)
        self.assertGreater(res["Weekday"]["total_revenue"], 0)
        self.assertGreater(res["Weekend"]["total_revenue"], 0)
        print("Passed.")

    def test_festive_normal(self):
        print("\nTesting Festive vs Normal Performance (Q7)...")
        res = compare_festive_normal()
        self.assertIn("periods", res)
        self.assertGreater(len(res["periods"]), 0)
        # Normal should be present
        period_types = [p["period_type"] for p in res["periods"]]
        self.assertIn("Normal", period_types)
        print("Passed.")

    def test_consistent_store_decline(self):
        print("\nTesting Consistent Store Decline (Q8 candidates)...")
        res = get_consistently_declining_stores()
        self.assertIsInstance(res, list)
        for store in res:
            trend = store["monthly_revenue"]
            self.assertEqual(len(trend), 3)
            # Mathematical condition: May > June > July
            self.assertGreater(trend[0]["revenue"], trend[1]["revenue"])
            self.assertGreater(trend[1]["revenue"], trend[2]["revenue"])
        print(f"Passed. Found {len(res)} consistently declining stores.")

    def test_percentage_change(self):
        print("\nTesting Percentage Change Calculations...")
        # (New - Old) / Old * 100
        # Check logic with test values
        old_val, new_val = 100.0, 120.0
        change = ((new_val - old_val) / old_val) * 100
        self.assertEqual(change, 20.0)
        
        old_val, new_val = 100.0, 80.0
        change = ((new_val - old_val) / old_val) * 100
        self.assertEqual(change, -20.0)
        print("Passed.")

    def test_aov_calculation(self):
        print("\nTesting AOV Calculation correctness...")
        # Check AOV matches revenue / orders on Q1
        res = get_last_n_month_metrics(3)
        calculated_aov = res["revenue"] / res["orders"]
        self.assertAlmostEqual(res["aov"], calculated_aov, places=2)
        print("Passed.")

if __name__ == "__main__":
    unittest.main()

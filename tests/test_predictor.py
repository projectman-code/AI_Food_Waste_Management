import unittest
from models.waste_predictor import predict_waste

class PredictorTests(unittest.TestCase):
    def test_surplus(self):
        result = predict_waste(20, 12, 2, 28)
        self.assertEqual(result["surplus_kg"], 8)
        self.assertGreater(result["risk"], 0)

    def test_no_surplus(self):
        result = predict_waste(5, 10, 8, 20)
        self.assertEqual(result["surplus_kg"], 0)

    def test_negative_rejected(self):
        with self.assertRaises(ValueError):
            predict_waste(-1, 2, 2, 20)

if __name__ == "__main__":
    unittest.main()

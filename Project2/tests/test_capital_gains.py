import unittest
import requests

class TestCapitalGainsService(unittest.TestCase):

    BASE_URL = "http://localhost:5003/capital-gains"

    def test_get_capital_gains(self):
        """Test retrieving capital gains"""
        response = requests.get(self.BASE_URL)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), float)

if __name__ == "__main__":
    unittest.main()
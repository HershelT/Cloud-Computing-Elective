import unittest
import requests

class TestStocks2Service(unittest.TestCase):

    BASE_URL = "http://localhost/stocks2"

    def test_create_stock(self):
        """Test creating a new stock"""
        stock_data = {
            "name": "Test Stock",
            "symbol": "TST",
            "purchase_price": 100.0,
            "purchase_date": "2023-01-01",
            "shares": 10
        }
        response = requests.post(self.BASE_URL, json=stock_data)
        self.assertEqual(response.status_code, 201)
        self.assertIn("_id", response.json())

    def test_get_stocks(self):
        """Test retrieving all stocks"""
        response = requests.get(self.BASE_URL)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_get_stock_by_id(self):
        """Test retrieving a stock by ID"""
        stock_id = "some_stock_id"  # Replace with a valid stock ID
        response = requests.get(f"{self.BASE_URL}/{stock_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("symbol", response.json())

    def test_update_stock(self):
        """Test updating a stock"""
        stock_id = "some_stock_id"  # Replace with a valid stock ID
        updated_data = {
            "name": "Updated Stock",
            "symbol": "TST",
            "purchase_price": 150.0,
            "purchase_date": "2023-01-01",
            "shares": 20
        }
        response = requests.put(f"{self.BASE_URL}/{stock_id}", json=updated_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["_id"], stock_id)

    def test_delete_stock(self):
        """Test deleting a stock"""
        stock_id = "some_stock_id"  # Replace with a valid stock ID
        response = requests.delete(f"{self.BASE_URL}/{stock_id}")
        self.assertEqual(response.status_code, 204)

if __name__ == "__main__":
    unittest.main()
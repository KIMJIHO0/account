import unittest
from pathlib import Path
import pandas as pd
from services import storage

class TestStorage(unittest.TestCase):
    def test_roundtrip(self):
        tmp = Path("data/test_transactions.csv")
        if tmp.exists():
            tmp.unlink()
        storage.ensure_csv(tmp)
        storage.append_row({"date":"2025-08-18","type":"지출","category":"식비","description":"테스트","amount":5000}, tmp)
        df = storage.read_all(tmp)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["amount"], 5000)
        tmp.unlink()

if __name__ == "__main__":
    unittest.main()

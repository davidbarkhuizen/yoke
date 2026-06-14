### solution.py
```python
def dicts_to_table(list_of_dicts: list[dict[str, str]]) -> str:
    if not list_of_dicts:
        return ""
    
    keys = list(list_of_dicts[0].keys())
    header = "| " + " | ".join(keys) + " |"
    separator = "| " + " | ".join(["---"] * len(keys)) + " |"
    
    rows = []
    for d in list_of_dicts:
        row = "| " + " | ".join(str(d[k]) for k in keys) + " |"
        rows.append(row)
        
    return "\n".join([header, separator] + rows)
```

### test_solution.py
```python
import unittest
from solution import dicts_to_table

class TestDictsToTable(unittest.TestCase):
    def test_basic_table(self):
        input_data = [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}]
        expected = "| name | age |\n| --- | --- |\n| Alice | 30 |\n| Bob | 25 |"
        self.assertEqual(dicts_to_table(input_data), expected)

    def test_empty_list(self):
        self.assertEqual(dicts_to_table([]), "")

    def test_single_dict(self):
        input_data = [{"col1": "val1"}]
        expected = "| col1 |\n| --- |\n| val1 |"
        self.assertEqual(dicts_to_table(input_data), expected)

if __name__ == "__main__":
    unittest.main()
```
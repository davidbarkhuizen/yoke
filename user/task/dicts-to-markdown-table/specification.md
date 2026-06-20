# convert list of python dictionaries to markdown table string

## inputs

- list of dictionaries to convert
  * `list[dict[str, str]]`
- alignment
  * str
  * allowed values: 'left', 'center', 'right'
  * default: 'center'

### input validation

- in the case of being sent an empty list, then return an empty string
- if any element in the list is None, then raise a ValueError
- check that all dictionaries in the list have the same keys
  * otherwise raise a ValueError exception
- raise a ValueError exception if a dictionary item key of None is encountered
- validate that alignment parameter is one of 'left', 'center', or 'right'
  * raise ValueError if invalid alignment provided
- ensure no duplicate keys exist within individual dictionaries
- all dictionary values must be convertible to strings (including None values)

## outputs

return a single multiline string that corresponds to a table in markdown format with:
- First row containing column headers (dictionary keys)
- Second row defining column alignment using hyphens and colons
- Subsequent rows containing data from dictionaries

## processing

### handling dictionary values

when retrieving a key value from a dictionary for conversion to a table row cell

- if the value is None
  * convert to empty string
- if the value is a string
  * return the value
- all other cases
  * convert value to string using str function

### special character handling

When values contain markdown syntax characters:
- Pipe characters (|) should be escaped with backslash (\|)
- Backslashes should be escaped with double backslash (\\)
- Newlines should be converted to HTML <br> tag for proper rendering in markdown
- Asterisks (*) and underscores (_) should be escaped when they appear at word boundaries
- Word boundary is defined as a character that is not alphanumeric or underscore

## markdown table format specification

Markdown tables structure data using pipe character (|) to separate columns and a row of three hyphens (---) to define the header.  This syntax is part of GitHub-Flavored Markdown (GFM) and is widely supported in documentation, wikis, and README files.

Basic Syntax To create a simple table, place headers in the first row, followed by a separator line, and then the data rows. Pipes are required at the start and end of each line for clarity

### example of basic syntax for markdown tables

| Name    | Age | City       |
|---------|-----|------------|
| Alice   | 25  | New York   |
| Bob     | 30  | London     |

### text alignment in markdown tables

Text Alignment You can control column alignment using colons (:) in the separator row. A colon on the left aligns text left, on the right aligns right, and on both sides centers the text.

#### example of text alignment in markdown tables

| Left  | Center | Right |
|:------|:------:|------:|
| Data1 | Data2  | Data3 |
| Data4 | Data5  | Data6 |

## edge cases

- Empty list input should return empty string
- All dictionary keys must be strings (as per type annotation)
- Duplicate keys within individual dictionaries are not allowed and should raise a ValueError during preprocessing
- None values in dictionaries are converted to empty strings during processing
- If any dictionary contains None as a key, raise ValueError
- Column headers maintain their original order from the first dictionary
- Empty dictionaries in the list should be treated as if they contain no data rows

```python
def dict_list_to_markdown_table(data: list[dict[str, str]], alignment: str = 'center') -> str:
    """
    Convert a list of dictionaries to a markdown table string.
    
    Args:
        data: List of dictionaries with consistent keys (all keys must be strings)
        alignment: Text alignment for columns ('left', 'center', or 'right')
        
    Returns:
        Markdown formatted table as string
        
    Raises:
        ValueError: If input validation fails (empty list, None values, inconsistent keys, invalid alignment, duplicate keys)
    """
    pass
```

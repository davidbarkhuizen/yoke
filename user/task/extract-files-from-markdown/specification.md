### specification

develop a python solution that processes a markdown document, extracting all fenced code sections preceded by file path markers (as defined below) to distinct text files on the file system.

- split the process into the following discrete phases
  * extraction of files with paths from markdown document
  * writing of extracted files

#### inputs

- file path to a source markdown document
  * in the form of a string
- folder path to a destination folder to write the extracted code files to 
  * in the form of a string

### processing

- load the source markdown document from the local file system
- scan through the markdown document, identifying all fenced code section
- for each fenced code section identified
  * check if that section is immediately preceded (previous line) by a file path marker (full format and examples defined later)
    - if it is, extract and set aside the file path and code section contents for further processing
    - in it is not, skip and continue to the next section
    - ignore code sections which that are empty or only whitespace
    - ignore any code section preceded by a file path marker that does not conform to the defined format
    - raise an exception if a duplicate file path marker is encountered
- after document parsing is complete, export the extracted code as files using the file paths
- for each extracted code file, i.e. (file path, code section) pair
  * write the contents of the code section to the local file system
  * write the file to a path indicated in the file path marker, relative to the destination folder
  * check that the ultimate file path is a actually child directory of the destination folder
    - raise an exception if the ultimate file path is not a child directory of the destination folder
  * write the file as a text file
    - if if the file already exists, then overwrite it

in general
- create folders if they don't already exist

### format of a file path marker

for file path xxx/yyy/zzz.py  

**`xxx/yyy/zzz.py`**

- markdown formatting: bold-inline-code 
- star-star-back_tick-{file_path}-back_tick-star-star

### format of a text file included in a markdown document

- each text file is included as a separate fenced code block in the markdown document
- the fenced code block for the text file with a given path is be immediately preceded in the markdown document (i.e. the previous line) by the file path marker in bold inline code format
  * e.g. **`xxx/yyy/zzz.py`**
  * the file path marker itself is not be preceded or followed by any whitespace
  * the fenced code block is not be indented
- the file path in the file path marker is a relative path, and not an absolute path
- the file path marker itself is immediately preceded by a blank line
- the fenced code block should be immediately followed by a blank line

Here is an example for a python code file `zzz.py` with relative file path `xxx/yyy/zzz.py`:

**`xxx/yyy/zzz.py`**
```python
def hello_world():
    print('hello world')
```

Here is an example for a python code file `dog.py` with relative file path `cat/fish/dog.py`:

**`cat/fish/dog.py`**
```python
def hello_world():
    print('hello world')
```

Here is an example for a sql code file `query.sql` with relative file path `cat/fish/query.sql`:

**`cat/fish/query.sql`**
```sql
select * 
from target_database.target_schema.target_table
where True
```

### outputs

a list of the destination paths of the successfully extracted files

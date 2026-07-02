# TODO

- support templates in system spec
  * to allow re-use / keep templates DRY
  * e.g. response format
  * e.g root system prompt should contain the current date and be shared by all system prompts

## spec driven development

1. distillation of specification
2. generation of natural language test cases based on specification 
2. generation of code tests from natural language test cases 
4. generation of code solution based on specification, that passes all tests


automations
- run find-and-fix-bugs xxx for each source file in xxx respectively in isolation
  * create report for each file
  * in order to handle large code-bases

auto-fix (single file)
- identify bugs in file
- determine which bugs have small, localised fixes
- for each such bug
  * do a targeted automated fix using the previous analysis
  * determine which other files in the code base would be affected
  * update those files
  * check if the solution still builds and passes tests - after the primary fix and first-order knock-on fixes in other files
    - fix any failing tests
      *

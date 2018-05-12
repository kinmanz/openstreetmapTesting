

## OpenStreetMap testing
 
**geoTester.py** is a Python script.

**Requirements:**
* Python 3.6
* requests library

```bash
pip install requests
```

#### How to use it?

* **--source** or **_-s_**
It's config data folder path.
The folder where all test configurations, our tool will use to run tests, are stored.
(default project folder **_testsConfigurations_**)
* **--threads** or **-t**
Number of threads you want to use to make API calls. (default 1)

```bash
geoTester.py
# or
geoTester.py -s ./testsConfigurations -t 1
```

### How to form config data folder?
Config data folder consist of configuration files in JSON format.
You can use files currently in the (**_testConfigurations_**) as example.
(or you can pass any folder on your file system, which has required files inside)
In that folder you can have only **.json** and **.MD/.md** files, 
json files need to be properly formatted (tool will check it before test).

Here I'd like to mention key formatting features.

```json
{
  "name" : "Russia geo mapping test",
  "ignore" : false,
  "test_cases" : [
    {
      "name" : "Москва Кремль",
      "address" : "Кремль, РФ",
      "test_address" : "Кремль, РФ", // or ["Кремль", "РФ"]
      "coordinates": ["58.741947", "29.8471943"],
      "epsilon" : "0000.2",
      "run_only": "[direct/backward/both]"
    }
  ]
}
```
* **name** is a test name that would be shown in the log
* **address** is a full place address tool will use for direct test
* **test_address** full or part place address tool will use for backward test,
in case if you choose full name address your test will match address name on equality,
if you decide to list parts of the address then tool will check that each name
presents in the address returned by API
* **coordinates** just coordinates of the test place, used in both
direct and backward test
* **epsilon** has two options: equality(==0) checks returned coordinates
to be at exact point specified at coordinates test field, and epsilon (> 0) checks
that coordinates are in coordinate square with size epsilon*2
* **run_only** as you can see you can run only direct or backward test
if you don specify the field, by default you get both. It worths to mention too,
that if you specify only direct test then tou don't have to specify _test_address_ field,
also if you specify only backward test then you don't have specify _address_ and _epsilon_ fields
* **ignore** is outer field to test cases, allow you to ignore whole test file, 
(I don't favor idea to add the field to the test case, 
since it can be set to the true and be forgotten eventually, 
if you want to skip test case, then comment it, it's more notable)


### Backlog
* incorporate PyCharm and the test tool, to be able to see test result as usual project tests
* add string feature similarity as one of the test address features 
* add parameter to tun only direct or backward tests
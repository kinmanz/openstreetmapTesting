import functools
import json
import time
from json import JSONDecodeError


class GeoTestingException(Exception):
    pass


class WrongFileFormat(GeoTestingException):
    pass


ALLOWED_KEYS_OUTER = {"name", "ignore", "test_cases"}
ALLOWED_KEYS_TEST_CASE = {"name", "address", "test_address", "coordinates", "epsilon", "run_only"}


def check_file(file_path):
    """
    Just a base protection from self foot shooting
    checks that file is in .md or .json format
    also checks .json format is parsable, and has required fields
    """

    # wrong file extension
    if not any(file_path.endswith(end) for end in (".md", ".MD", ".json")):
        raise WrongFileFormat(
            "Wrong file format, expected json, or md,"
            + " got file with name {}".format(file_path))

    if any(file_path.endswith(end) for end in (".md", ".MD")):
        return

    with open(file_path) as test_pack_file:
        try:
            pack_content = json.loads(test_pack_file.read())
            if len(pack_content.keys() | ALLOWED_KEYS_OUTER) != len(ALLOWED_KEYS_OUTER):
                raise WrongFileFormat("Not allowed keys: {}"
                                      .format(pack_content.keys() - ALLOWED_KEYS_OUTER))
            if "name" not in pack_content or not isinstance(pack_content["name"], str):
                raise WrongFileFormat("Test pack name must be String and must be specified!")
            if "ignore" in pack_content and not isinstance(pack_content["ignore"], bool):
                raise WrongFileFormat("Ignore field must be 'bool'!")
            if "test_cases" in pack_content and not isinstance(pack_content["test_cases"], list):
                raise WrongFileFormat("test_cases field must be 'list'!")

            for case in pack_content["test_cases"]:
                # check test case fields
                if len(case.keys() | ALLOWED_KEYS_TEST_CASE) != len(ALLOWED_KEYS_TEST_CASE):
                    raise WrongFileFormat("Not allowed keys for test case: {}"
                                          .format(case.keys() - ALLOWED_KEYS_TEST_CASE))
                if "name" not in case or not isinstance(case["name"], str):
                    raise WrongFileFormat("Test case name must be String and must be specified!")
                if "coordinates" not in case or not isinstance(case["coordinates"], list) \
                        or len(case["coordinates"]) != 2:
                    raise WrongFileFormat("coordinates field must be pair of values and must be specified!")
                lat, lon = case["coordinates"]
                # check on ValueError
                float(lat)
                float(lon)
                if "epsilon" in case and not isinstance(case["epsilon"], str):
                    raise WrongFileFormat("epsilon must be string with float value")
                if "epsilon" in case:
                    float(case["epsilon"])

        except JSONDecodeError as e:
            #  not parsable JSON
            raise WrongFileFormat(e, "JSON is not parsable!")
        except ValueError as e:
            raise WrongFileFormat(e, "Coordinates and epsilon fields must be strings with float number!")


LOG_SPLIT_LINE_HEAD = "###" * 20


def header_splited_log(function):
    # add LOG_SPLIT_LINE_HEAD lines before and after fun invocation
    def wrapper(*args, **kwargs):
        print(LOG_SPLIT_LINE_HEAD)
        result = function(*args, **kwargs)
        print(LOG_SPLIT_LINE_HEAD)
        return result

    return functools.update_wrapper(wrapper, function)


def timing_log(function):
    # add time log to function invocation
    def wrapper(*args, **kwargs):
        start = time.time()
        result = function(*args, **kwargs)
        end = time.time()
        print("Execution time is {} seconds".format(end - start))
        return result

    return functools.update_wrapper(wrapper, function)

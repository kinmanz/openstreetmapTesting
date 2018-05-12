import argparse
import os
from multiprocessing import Semaphore
from multiprocessing.pool import Pool

import requests

from geoTesterUtils import *

# PLEASE read README.MD before going through the code

# used to sync print statements
SCREENLOCK = Semaphore(value=1)

# Протестировать необходимо прямое (адрес -> координаты)
# и обратное (координаты -> адрес) геокодирование.
# Предпочтительные языки разработки: python.

LOG_SPLIT_LINE_CONTENT = "---" * 20

API_URL = "https://nominatim.openstreetmap.org"

parser = argparse.ArgumentParser(description='geoTester')
parser.add_argument('-s', '--source', help='Source folder', default="./testsConfigurations", required=False)
parser.add_argument('-t', '--threads', help='Threads number', default="1", required=False)
args = vars(parser.parse_args())

TEST_FOLDER_PATH = args["source"]
THREADS_NUMBER = int(args["threads"])

# decorators for logging and timing

print("Started")
print("TEST_FOLDER_PATH: {}".format(TEST_FOLDER_PATH))
print("THREADS_NUMBER: {}".format(THREADS_NUMBER))


def run_test_case_direct(test_case):
    test_output = "->->-> Direct ->->->\n"
    query_params = {
        "format": "json",
        "q": test_case["address"]
    }
    api_call_results = json.loads(requests.get(API_URL, params=query_params).content)
    status = False
    for api_call_res in api_call_results:
        expected_lat, expected_lon = map(float, test_case["coordinates"])
        actual_lat, actual_lon = map(float, (api_call_res["lat"], api_call_res["lon"]))
        epsilon = float(test_case["epsilon"])
        test_output += "Got coordinates: {}\n".format(test_case["coordinates"])
        test_output += "Expected to see: {}\n".format([actual_lat, actual_lon])
        if abs(actual_lat - expected_lat) <= epsilon and abs(actual_lon - expected_lon) <= epsilon:
            status = True
    test_output += ("SUCCESSFUL" if status else "FAILURE")
    return status, test_output


def run_test_case_backward(test_case):
    test_output = "<-<-<- Backward <-<-<-\n"
    query_params = {
        "format": "json",
        "q": " ".join(test_case["coordinates"])
    }
    api_call_results = json.loads(requests.get(API_URL, params=query_params).content)
    status = False
    for api_call_res in api_call_results:
        expected_address = test_case["test_address"]
        actual_address = api_call_res["display_name"]
        test_output += "Got place name: \"{}\"\n".format(actual_address)
        test_output += "Expected to see: {}\n".format(expected_address)
        status = all(adr in actual_address for adr in expected_address) \
            if isinstance(expected_address, list) else expected_address == actual_address
    test_output += "SUCCESSFUL" if status else "FAILURE"
    return status, test_output


def run_test_case(test_case):
    """
    :param test_case:
    :return "success/fail"
    """
    res = []
    test_output = []
    if "run_only" not in test_case or test_case["run_only"] == "direct":
        status, out = run_test_case_direct(test_case)
        res.append(status)
        test_output.append(out)
    if "run_only" not in test_case or test_case["run_only"] == "backward":
        status, out = run_test_case_backward(test_case)
        res.append(status)
        test_output.append(out)

    SCREENLOCK.acquire()
    print(LOG_SPLIT_LINE_CONTENT)
    print("Test case: {}".format(test_case["name"]))
    print("\n".join(test_output), flush=True)
    print(LOG_SPLIT_LINE_CONTENT)
    SCREENLOCK.release()

    return all(res)


@header_splited_log
def run_test_pack(test_pack_path):
    """
    :param test_pack_path:
    :return (tests have run, failures)
    run .json pack
    """
    # TODO put it in decorator
    with open(test_pack_path) as test_pack_file:
        pack_content = json.loads(test_pack_file.read())
        print(pack_content["name"])
        res = []
        if pack_content.get("ignore", False):
            print("PACK IGNORED")
            return res
        with Pool(THREADS_NUMBER) as pool:
            res = pool.map(run_test_case, (test_case for test_case in pack_content["test_cases"]))
            # for test_case in pack_content["test_cases"]:
            #     res.append(run_test_case(test_case))
    print("TEST PACK REPORT: tests: {}, failures: {}".format(len(res), sum(1 for r in res if not r)))
    return res


@timing_log
def run_tests(test_folder_path):
    # get all files in test folder
    test_folder_files = os.listdir(test_folder_path)
    # check them
    for file_name in test_folder_files:
        check_file(os.path.join(test_folder_path, file_name))
    test_packs = list(filter((lambda fn: fn.endswith(".json")), test_folder_files))
    # show test packs
    print("\nTEST PACKS:")
    print(*test_packs, sep="\n", end="\n\n")

    # do test
    final_report_tests = 0
    final_report_fails = 0
    for test_pack in test_packs:
        res = run_test_pack(os.path.join(test_folder_path, test_pack))
        final_report_tests += len(res)
        final_report_fails += sum(1 for r in res if not r)
    print("OVERALL STATUS: {}".format("SUCCESS" if final_report_fails == 0 else "FAIL"))
    print("TESTS: {}, FAILS: {}".format(final_report_tests, final_report_fails))


run_tests(TEST_FOLDER_PATH)

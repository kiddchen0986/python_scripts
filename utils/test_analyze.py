"""Module containing tools to analyze test results"""
from wrapper.prodtestlib.prodtestlib_common import FPCErrorCode


def calculate_yield(test_seq_packs, analyze_container=None):
    """Calculates the yield of the test results by dividing the number of passed tests subtracted by the number of
    tests. Also adds the number_of_tests, passed_tests and failed_tests to analyze_container.

    :param test_seq_packs: list of test_sequence_packages
    :type test_seq_packs: list of dicts
    :param analyze_container: dict of analyzed values
    :type analyze_container: dict
    :return: dict of analyzed values (analyze_container)
    :rtype: dict
    """
    if analyze_container is None:
        analyze_container = {}

    passed_tests = 0
    for test_seq in test_seq_packs:
        if test_seq["pass"]:
            passed_tests += 1

    analyze_container["yield"] = round(passed_tests / len(test_seq_packs), 3)
    analyze_container["number_of_tests"] = len(test_seq_packs)
    analyze_container["passed_tests"] = passed_tests
    analyze_container["failed_tests"] = analyze_container["number_of_tests"] - passed_tests

    return analyze_container


def compile_errors(test_seq_packs, analyze_container=None):
    """Counts how many of each individual error, adds as a dict to the analyze container

    :param test_seq_packs: list of test_sequence_packages
    :type test_seq_packs: list of dicts
    :param analyze_container: dict of analyzed values
    :type analyze_container: dict
    :return: dict of analyzed values (analyze_container)
    :rtype: dict
    """
    if analyze_container is None:
        analyze_container = {}

    compiled_errors = {}

    ok_errors = [FPCErrorCode.FPC_OK]

    for seq_pack in test_seq_packs:

        for error in seq_pack["error_code"]:
            if error not in ok_errors:

                if error in compiled_errors:
                    compiled_errors[error] += 1
                else:
                    compiled_errors[error] = 1

    analyze_container["nbr_errors"] = compiled_errors
    return analyze_container

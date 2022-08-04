import argparse
import os
from os import walk

ROOT_FOLDER = os.getcwd()
PATH_TO_SOLUTION = os.path.join(ROOT_FOLDER, "app", "src", "androidTest", "java")
SUBPATH_TO_TESTCASES = os.path.join("com", "fingerprints", "automation", "testcases")

test_cases = []
features_to_exclude = ["Ignore"]
not_supported_features = {
    "fpc1291_g175": ["CheckerboardTest"],
    "fpc1075": ["DefectivePixelsTest"],
    "fpc1028": ["DefectivePixelsTest"],
    "fpc1235": ["DefectivePixelsTest"],
    "fpc1025": ["DefectivePixelsTest"],
    "fpc1035": ["DefectivePixelsTest"],
    "fpc1145": ["DefectivePixelsTest"],
    "fpc1245": ["DefectivePixelsTest"],
    "fpc1262": ["DefectivePixelsTest"],
    "fpc1266": ["DefectivePixelsTest"],
    "fpc1511": ["CheckerboardTest"],
    "fpc1521": ["CheckerboardTest"],
    "fpc1541": ["CheckerboardTest"],
    "fpc1542_s": ["CheckerboardTest"],
    "fpc1542_c160": ["CheckerboardTest"],
    "fpc1511_g175": ["CheckerboardTest"],
    "fpc1268": ["LowCoverageAndQuality", "DefectivePixelsTest"]
}


def __create_exclude_list(model, enroll, sensortest, manifest, sensor):
    """ Creates a list of excluded features depending on sensor, model and features enabled in SW """
    if model == "hikey" or model == "hikey960":
        features_to_exclude.append("Hammerhead")
    if not enroll:
        features_to_exclude.append("IdentifyAtEnroll")
    if not sensortest:
        features_to_exclude.append("ImageToolTest")
    if "sw23.1" in manifest or "sw22" in manifest:
        features_to_exclude.append("ProgressInDiagLog")

    for s, features in not_supported_features.items():
        if s == sensor:
            features_to_exclude.extend(features)

    print("\nFeatures to exclude: {}".format(features_to_exclude))


def __collect_test_cases():
    """
    Collects sub paths to all files containing SYSTA in their name. The path will include
    com/fingerprints/automation/testcases/[test case folder]/[test case name]
    """
    for (dirpath, dirnames, filenames) in walk(os.path.join(PATH_TO_SOLUTION, SUBPATH_TO_TESTCASES)):
        test_cases.extend([os.path.join(SUBPATH_TO_TESTCASES, os.path.basename(dirpath), f) for f in filenames if "SYSTA" in f])


def __exclude_test_cases():
    """ Excludes test cases with annotations that matches the excluded features list """
    test_cases_to_exclude = []
    for tc in test_cases:
        file = open(os.path.join(PATH_TO_SOLUTION, tc), 'r')
        for line in file:
            if any(("@" + f) in line for f in features_to_exclude):
                test_cases_to_exclude.append(tc)
                break
        file.close()

    print("\nExcluding test cases: " + str(len(test_cases_to_exclude)))
    for tc in test_cases_to_exclude:
        print(tc)
        test_cases.remove(tc)


def __create_java_file():
    """ Creates a test suite (java file) based on the test cases that should be executed """
    with open(os.path.join(PATH_TO_SOLUTION, SUBPATH_TO_TESTCASES, "TestSuite.java"), "w") as writer:
        writer.write("package com.fingerprints.automation.testcases;\n")
        writer.write("\n")
        writer.write("import org.junit.runner.RunWith;\n")
        writer.write("import org.junit.runners.Suite;\n")

        # Import all test cases
        for tc in test_cases:
            tc = tc.replace(".java", "").replace(os.path.sep, ".")
            writer.write("import {}{}{}".format(tc, ";", "\n"))

        writer.write("\n")
        writer.write("@RunWith(Suite.class)\n")
        writer.write("@Suite.SuiteClasses({\n")

        # Add test cases to suite
        for tc in test_cases:
            tc = os.path.split(tc)[1] # Returns only file name
            tc = tc.replace(".java", ".class")
            writer.write("\t" + tc + "," + "\n")

        writer.write("})\n")
        writer.write("\n")
        writer.write("public class TestSuite {\n")
        writer.write("}\n")
        writer.close()


def start(sensor, model, manifest, enroll, sensortest, testcase):
    if testcase is not None:
        # Only run the selected test case(s)
        for tc in testcase.split(","):
            test_cases.append(tc.replace(".", os.path.sep) + ".java")

    else:
        # Run all test cases
        __collect_test_cases()
        features_to_exclude.extend(["KPI", "PSV"]) # Exclude KPI and PSV from regular execution

    print("\nTest cases before exluding: " + str(len(test_cases)))
    print("\n".join(tc for tc in test_cases))

    __create_exclude_list(model, enroll, sensortest, manifest, sensor)
    __exclude_test_cases()

    print("\nTest cases to execute: " + str(len(test_cases)))
    print("\n".join(tc for tc in test_cases))

    __create_java_file()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--sensor', '-f', required=True, help='Sensor target')
    parser.add_argument('--model', '-m', required=True, help='Model target')
    parser.add_argument('--manifest', '-mv', required=True, help='Manifest version')
    parser.add_argument('--enroll', '-r', required=True, help='_IDENTIFY_AT_ENROL_')
    parser.add_argument('--sensortest', '-st', required=True, help='_SENSORTEST_')
    parser.add_argument('--testcase', '-tc', required=False, help='Run specific test case(s)')

    args = parser.parse_args()
    args.model = args.model.lower()
    args.sensor = args.sensor.lower()
    args.manifest = args.manifest.lower()

    start(args.sensor, args.model, args.manifest, args.enroll, args.sensortest, args.testcase)








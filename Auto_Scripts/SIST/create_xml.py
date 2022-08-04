import os
import datetime


# Creating an html file just containing the success percent
def create_html(total_tests, failed_tests, filepath):
    os.makedirs(filepath, exist_ok=True)
    success = total_tests - failed_tests
    percent = int((100.0) * (success / total_tests))

    with open(os.path.join(filepath, "index.html"), "w") as writer:
        writer.write("<div class='percent'>%s%%</div>" % percent)
        print("HTML created: index.html")


# Creates an XML with the results of all tests
def create_xml(nbr_tests, tests_executed, failed, filepath_xml):
    os.makedirs(filepath_xml, exist_ok=True)
    with open(os.path.join(filepath_xml, "com.fingerprints.si.tests.junit.xml"), "w") as writer:
        writer.write(
            '<testsuite name="com.fingerprints.si.tests" tests="%s" failures="%s" errors="0" skipped="0" time="0" timestamp="%s" hostname="localhost">\n' % (
                nbr_tests, failed, datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")))
        writer.write(
            '    <properties>\n        <property name="device" value="AOSP on HammerHead - 6.0.1"/>\n        <property name="flavor" value=""/>\n        <property name="project" value="app"/>\n    </properties>\n')
        for test in tests_executed:
            if test["failure"] != "":
                writer.write(
                    '<testcase name="%s" classname="%s" time="0">\n' % (
                        test["name"], test["classname"]))
                writer.write("    <failure>\n%s\n    </failure>\n" % test["failure"])
                writer.write('</testcase>\n')
            else:
                writer.write('<testcase name="%s" classname="%s.%s" time="0"/>\n' % (
                    test["name"], test["classname"], test["name"]))
        writer.write('</testsuite>')
    print("XML created: com.fingerprints.si.tests.junit.xml")


# Checks if a test case already exists in 'test'
def check_tests(tests, testcase):
    for test in tests:
        if testcase in test["name"]:
            return test
    return None


# Parses a file and extracts all test to an list
def parse_report(input):
    print("Parsing %s" % input)
    tests = []
    current_fail = {}
    num_testcases = 0
    num_testcases_found = False

    inputfile = open(input, 'r')
    lines = inputfile.readlines()
    inputfile.close()
    nbr_lines = len(lines)
    curr_line = 0

    while curr_line < nbr_lines:
        line = lines[curr_line].strip()

        if "numtests=" in line and not num_testcases_found:
            num_testcases = int(line.split("=")[1])
            num_testcases_found = True

        if line.startswith("INSTRUMENTATION_STATUS: test"):  # Test case found
            testname = line[line.rfind("=") + 1:]
            curr_line += 1
            line = lines[curr_line].strip()
            if line.find("INSTRUMENTATION_STATUS: class") == -1:
                curr_line += 1
                line = lines[curr_line].strip()
            classname = line[line.rfind("=") + 1:]
            classname = classname[:classname.rfind(".")]
            testcase_exists = check_tests(tests, testname)  # Check if we have already saved this test case
            if testcase_exists is None:  # Test does not already exist, add it
                tests.append({"name": testname, "classname": classname, "time": "0", "failure": ""})

        elif line.startswith("Error in"):  # Error found
            testname = line[line.find("Error in") + 9:line.find("(com.")]
            classname = line[line.find("com."):-2]
            testcase_exists = check_tests(tests, testname)  # Check if this test cases is already saved
            if testcase_exists is None:  # Test does not exist, add new entry
                current_fail = {"name": testname, "classname": classname, "time": "0", "failure": ""}
                tests.append(current_fail)
            else:  # Test does exist, set current fail to existing test
                current_fail = testcase_exists

        elif ") com" in line:
            testname = "test_" + line[line.rfind("SYSTA"):]
            classname = line[3:line.rfind(".SYSTA")]
            testcase_exists = check_tests(tests, testname)  # Check if this test cases is already saved
            if testcase_exists is None:  # Test does not exist, add new entry
                current_fail = {"name": testname, "classname": classname, "time": "0", "failure": ""}
                tests.append(current_fail)
            else:  # Test does exist, set current fail to existing test
                current_fail = testcase_exists

        # If line empty, go to next line
        elif line.strip() == "":
            curr_line += 1
            continue

        # Something is really wrong
        elif "INSTRUMENTATION_ABORTED" in line.strip():
            raise Exception("Something went really wrong")

        # Continue reading the failure
        elif "failure" in current_fail:
            if line.startswith("INSTRUMENTATION_STATUS: id=AndroidJUnitRunner") or "Test mechanism" in line:
                current_fail["failure"] = current_fail["failure"].rstrip("\n")
                current_fail = {}
            else:
                current_fail["failure"] += line.replace("&", "&amp;") + "\n"

        curr_line += 1

    if len(tests) > 0:
        failed = 0
        for test in tests:  # Count nbr of failures
            if test["failure"] != "":
                failed += 1
        if num_testcases_found:
            return num_testcases, tests, failed
        else:
            raise Exception("Number of test cases to execute not found in log")
    else:
        raise Exception("Failed to find any tests in the report")


def start():
    ROOT_FOLDER = os.path.split(os.getcwd())[0]
    XML_FOLDER = os.path.join(ROOT_FOLDER, "SI", "app", "build", "outputs", "androidTest-results", "connected")
    HTML_FOLDER = os.path.join(ROOT_FOLDER, "SI", "app", "build", "reports", "androidTests", "connected")

    nbr_tests_to_execute, tests_executed, nbr_failed = parse_report("android/testReport.txt")

    if len(tests_executed) < nbr_tests_to_execute:
        nbr_failed += nbr_tests_to_execute - len(tests_executed)

    create_xml(nbr_tests_to_execute, tests_executed, nbr_failed, XML_FOLDER)
    create_html(nbr_tests_to_execute, nbr_failed, HTML_FOLDER)


if __name__ == "__main__":
    start()

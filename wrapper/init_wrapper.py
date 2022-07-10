"""Contains the functionality needed to initiate usage of a .dll library"""
import os
import ctypes as c
import re
from wrapper.wrapper_common import ErrorCode

PRODTESTLIB_MTT_VERSIONS = {8.1: "ModuleTestTool 8.1\\prodtestlib.dll",
                            9.1: "MTT 9.1\\prodtestlib.dll",
                            10.0: "MTT 10.0\\prodtestlib.dll",
                            11.0: "MTT 11.0\\prodtestlib.dll",
                            12.0: "MTT_12.0\\prodtestlib.dll"}  #: Checked in versions of Module Test Tool (MTT)

CURRENT_MTT_DIRECTORY = ErrorCode.MTT_NOT_INITIALIZED


def create_api(lib_file_path):
    """Creates the ctype API file needed to call functions in a .dll library

    :param lib_file_path: path to a .dll file
    :type lib_file_path: str
    :return: the python to C API
    :rtype: loaded library
    """

    current_wdr = os.getcwd()
    directory, file = os.path.split(lib_file_path)
    os.chdir(directory)
    libc = c.CDLL(file)
    os.chdir(current_wdr)

    print("Loaded {}".format(lib_file_path))

    return libc


def load_mtt_version(version=None):
    """Loads the prodtestlib.dll for the given MTT (Module Test Tool) version

    :param version: the version number
    :type version: number
    :return: the python to C API
    :rtype: ctypes API object
    """
    backup_version = max(PRODTESTLIB_MTT_VERSIONS.keys())
    if version is None:
        version = backup_version

    current_wdr = os.getcwd()
    pattern = ".+?(?=python_scripts)"
    search_object = re.match(pattern, current_wdr)
    mtt_directory = os.path.join(search_object.group(0), "python_scripts", "wrapper", "binaries")
    try:
        file_path = os.path.join(mtt_directory, PRODTESTLIB_MTT_VERSIONS[version])
    except KeyError:
        print("MTT version {} is not supported, using {} instead.".format(version, backup_version))
        file_path = os.path.join(mtt_directory, PRODTESTLIB_MTT_VERSIONS[backup_version])

    global CURRENT_MTT_DIRECTORY
    CURRENT_MTT_DIRECTORY = os.path.dirname(file_path)

    return create_api(file_path)


def retrieve_path_to_mtt_version(v=None):
    """Returns the file path to the directory of the MTT version. If version is not provided, takes the newest version

    :param v: the mtt version
    :type v: float
    """
    backup_version = max(PRODTESTLIB_MTT_VERSIONS.keys())
    if v is None:
        v = backup_version

    current_wdr = os.getcwd()
    pattern = ".+?(?=python_scripts)"
    search_object = re.match(pattern, current_wdr)
    mtt_directory = os.path.join(search_object.group(0), "python_scripts", "wrapper", "binaries")
    try:
        file_path = os.path.join(mtt_directory, PRODTESTLIB_MTT_VERSIONS[v])
    except KeyError:
        print("MTT version {} is not supported, using {} instead.".format(v, backup_version))
        file_path = os.path.join(mtt_directory, PRODTESTLIB_MTT_VERSIONS[backup_version])

    global CURRENT_MTT_DIRECTORY
    CURRENT_MTT_DIRECTORY = os.path.dirname(file_path)

    return os.path.split(file_path)[0]







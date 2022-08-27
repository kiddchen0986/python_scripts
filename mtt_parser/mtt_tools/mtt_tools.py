""" MTT_tools

Tools for parsing MTT logs.

"""
import os
import sys
import inspect
PATH = "/".join(inspect.stack()[0][1].split("/")[:-3])
if PATH not in sys.path:
    sys.path.insert(0,PATH) #allow imports from top level
import utils.histogram as hist
import json
import pprint
import re
import warnings
from tkinter import *
from tkinter import messagebox



class parser():
    """
    MTT log parser.

    Methods
    -------
    init(path, target_params, ctl, profile)
        Initialize parser with specified data object. Must be called before
        parse().
    load_profile(profile)
        When specified, loads profile. Populates target_params with parameters.
    parse(data_format)
        Start parsing using specified format.
    parse_json(item, origin, level)
        Do not call directly. Method is called from parse().
    parse_html(data, filename)
        Do not call directly. Method is called from parse()
    analyze_preferred_file_format()
        Analyze which data format to use when unspecified from user.

    """

    def __init__(self, data):
        """Constructor

        Create parser object with specified data object

        Parameters
        ----------
        data : mtt_tools:data
            The data object in which all parsed data will reside.
        """
        self.data = data
        self.init_complete = False

    def init(self, path_to_folder, target_params=[], ctl=False, profile=""):
        """Initialize parser.

        The parser initializes by gathering metadata and prepares to parse. The
        information gathered is stored in the associated data object and can be
        used to customize the parsing. If target_params is specified all other
        parameters are disregarded. Same goes for profile.

        Parameters
        ----------
        path_to_folder : str
            Path to folder,relative to script location, containing parsable
            files.
        target_params : list, optional
            List with string representations of which parameters the parser
            should look for, e.g. "TestTimeMilliseconds". If not specified all
            parameters are included.
        ctl : bool
            Set true if Common Test Library (CTL) was used to generate the logs.
        profile : str
            Name of profile to use. File must be in the /profiles folder.

        Examples
        --------
        >>> init("path/to/folder")
        """
        print("initializing...")
        if not os.path.exists(path_to_folder):
            raise IOError("Invalid path: "+path_to_folder)
        self.data.path_to_folder = path_to_folder
        self.data.filelist = []
        self.data.tests = []
        self.data.files = dict()
        self.data.target_params = target_params
        self.data.ctl = ctl
        self.data.debug = []
        self.data._meta = {}
        self.data._meta['subtest_result'] = {}
        self.data._meta['test_result'] = [] #where whole test results are stored
        self.data._meta['subtests'] = [] #for parsing subtest_result
        self.data.hashes = []
        warnings.simplefilter("ignore", category=PendingDeprecationWarning)

        if profile:
            self.load_profile(profile)

        for path, _, files in os.walk(path_to_folder):
            for name in sorted(files):
                _, file_extension = os.path.splitext(os.path.join(path, name))
                if file_extension in self.data.files:
                    self.data.files[file_extension] += 1
                else:
                    self.data.files[file_extension] = 1
                filename = os.path.join(path, name)
                self.data.filelist.append(filename)
                if file_extension == ".json":
                    try:
                        with open(filename, encoding='utf-8') as file:
                            json_data = json.load(file)
                            if ctl:
                                for entry in json_data['sequence']:
                                    if entry['test_name'] not in self.data.tests:
                                        self.data.tests.append(entry['test_name'])
                            else:
                                for entry in json_data['TestReportItems']:
                                    if entry['Name'] not in self.data.tests:
                                        self.data.tests.append(entry['Name'])
                    except NameError:
                        pass
                    except ValueError:
                        print(filename)
                    except KeyError:
                        print("Could not parse test names.")
        self.data.print_file_ext()
        self.init_complete = True

    def load_profile(self, profile):
        """ Loads profile.
        """
        path_to_profiles = "profiles/"+profile
        cur_block = ""
        with open(path_to_profiles, encoding='utf-8') as file:
            options = file.read().splitlines()
            for opt in options:
                try:
                    if opt[0]=="[":
                        cur_block=opt
                    else:
                        if not opt[0]=="#": #ignore commented lines
                            if cur_block=="[Config]":
                                pass
                            elif cur_block=="[Parameters]":
                                self.data.target_params.append(opt)
                except IndexError: #blank line
                    pass


    def parse(self, data_format="auto"):
        """Start parsing.

        Can only be called after initializion.

        Parameters
        ----------
        data_format : str, optional
            The format of the parsable logs. Tries to auto-detect if
            unspecified.

        Raises
        ------
        NotInitializedError
            When parse() is called before init()
        """
        if not self.init_complete:
            raise NotInitializedError("parse() called before init().")

        if data_format == "auto":
            data_format = self.analyze_preferred_file_format()
            if not data_format:
                raise UnsupportedFileFormatError("Found no parsable files in "+
                                                 "specified folder. Make sure"+
                                                 "target folder contains "+
                                                 "supported file types.")
        else:
            if data_format not in self.data.files.keys():
                raise UnsupportedFileFormatError("*" + data_format + "* file " +
                                                 "extension not found in "+
                                                 "specified folder.")
            else:
                self.data.selected_ext = data_format

        print("Parsing " + self.data.path_to_folder + " using " + data_format + " format....")
        for filename in self.data.filelist:
            if filename.endswith(data_format):
                with open(filename, encoding='utf-8') as file:
                    try:
                        if data_format == ".json":
                            data = file.read()
                            self.data.hashes.extend([(hash(data), filename)])
                            json_data = json.loads(data)
                            self.parse_json(json_data, "", 0)
                        elif data_format == ".html":
                            self.parse_html(file.read(), filename)
                    except ValueError:
                        print("json not valid")

        print("Parsing done. " + str(self.data.files[data_format]) + " files parsed.")
        self.data.print_tests()
        self.data.test_status()
        if self.data.selected_ext == ".html":
            self.data.available_data()

    def parse_html(self, data, filename):
        """Parse data in html format.

        Parse data and add parameters to the linked data object.

        Parameters
        ----------
        data : str
            Contents of loaded file.
        filename : str
            Name of file loaded
        """
        unihash = hash(data)
        self.data.hashes.extend([(unihash, filename)])
        if 'SensorId' not in self.data.data.keys():
            self.data.data['SensorId'] = []
        if 'test_result' not in self.data._meta.keys():
            self.data._meta['test_result'] = []

        self.data._meta['test_result'].extend(
            [(unihash, data.split("<b> Test Result: </b>")[1].split("</font><br>")[0]
              .split(">")[1])])

        sensor_id = data.split("<b> Sensor ID: </b>")[1].split("<br>")[0]
        self.data.data['SensorId'].extend([(unihash, sensor_id)])

        data_s = data.split("</h3>")[2].split("<br>\n")
        for part in data_s:
            if re.search("Pass", part) or re.search("Fail", part):
                subpart = part.split("<b>")
                subtest = subpart[0].split(":")[0].replace(" ", "_").lower()
                pf = subpart[1].split("</b>")[0]
                if subtest not in self.data._meta['subtest_result'].keys():
                    self.data._meta['subtest_result'][subtest] = [(unihash, pf)]
                else:
                    self.data._meta['subtest_result'][subtest].extend([(unihash, pf)])

            for target in self.data.target_params:
                if re.search(target, part):
                    k = part.split(": ")[1]
                    r = re.compile("\d*\.?\d*")
                    value = float(r.findall(k)[0])
                    key = target.replace(" ", "_").lower()
                    if target == "Number of blobs pixels":
                        lim_value = float(part.split("(limit: ")[1].split(")")[0])
                        if key not in self.data.data.keys():
                            self.data.data[key+"_limit"] = [(unihash, lim_value)]
                        else:
                            self.data.data[key+"_limit"].extend([(unihash, lim_value)])
                    if key not in self.data.data.keys():
                        self.data.data[key] = [(unihash, value)]
                    else:
                        self.data.data[key].extend([(unihash, value)])

    def analyze_preferred_file_format(self):
        """Analyze and pick files to parse

        """
        extensions = self.data.files
        if ".json" in extensions.keys():
            self.data.selected_ext = ".json"
            return ".json"
        elif ".html" in extensions.keys():
            self.data.selected_ext = ".html"
            return ".html"
        else:
            return ""

    def parse_json(self, item, origin, level):
        """Recursive walk through json structure.

        Walk recursively through json structure and add parameters to the
        parsers data object.

        Parameters
        ----------
        item : iterative object
            Current dict or list
        origin : str
            Current test name. Used to distinguish parameters with the same name
        level : int
            Current recursive level. Increases by 1 for each recursive call.
            Starts at 0.
        """
        cur_hash = self.data.hashes[-1][0]
        if isinstance(item, dict):
            for key in item.keys():
                if key == "TestName" or key == "test_name":
                    origin = item[key]+":"
                if key == "Success":
                    self.data._meta['test_result'].extend([(cur_hash, item[key])])
                if key == "TestMethodConclusion":
                    test_name = origin.split(":")[0].replace(" ", "_")
                    if test_name in self.data._meta['subtest_result'].keys():
                        self.data._meta['subtest_result'][test_name].extend([(cur_hash, item[key])])
                    else:
                        self.data._meta['subtest_result'][test_name] = [(cur_hash, item[key])]
                if key == "conclusion" and self.data.ctl:
                    if origin == "":
                        self.data._meta['test_result'].extend([(cur_hash, item[key])])
                    else:
                        if origin in self.data._meta['subtest_result'].keys():
                            self.data._meta['subtest_result'][origin].extend([(cur_hash, item[key])])
                        else:
                            self.data._meta['subtest_result'][origin] = [(cur_hash, item[key])]
                if isinstance(item[key], dict):
                    if ("d") in item[key].keys():
                        self.parse_json(item[key], origin+key+":", level+1)
                    else:
                        self.parse_json(item[key], origin, level+1)
                elif isinstance(item[key], list):
                    only_values = True
                    for value in item[key]:
                        if type(value) in (list, dict):
                            only_values = False
                    if only_values:
                        self.parse_json(item[key], origin+key, level+1)
                    else:
                        self.parse_json(item[key], origin, level+1)

                else:
                    if key in self.data.target_params or not self.data.target_params:
                        if origin+key in self.data.data:
                            self.data.data[origin+key].extend([(cur_hash, item[key])])
                        else:
                            self.data.data[origin+key] = [(cur_hash, item[key])]
            return
        elif isinstance(item, list):
            for x in item:
                self.parse_json(x, origin, level+1)
        else:
            if origin.split(":")[-1] in self.data.target_params or not self.data.target_params:
                if origin in self.data.data.keys():
                    match_found=False
                    for l in self.data.data[origin]:
                        print(origin)
                        if cur_hash == l[0]:
                            l[1].extend([item])
                            match_found = True
                    if not match_found:
                        self.data.data[origin].extend([(cur_hash, [item])])
                else:
                    self.data.data[origin] = [(cur_hash, [item])]

class data():
    """
    MTT data object.

    Keeper of all parsed data. The class has several helper methods which
    allows the user to extract relevant information about the parsed MTT data.

    Methods
    -------
    print_filenames()
        Print filenames of files that are prepared for parsing.
    print_tests()
        Print the MTT tests that has data in the prepared files.
    print_file_ext()
        Print information about the target files and their extensions.
    available_data()
        Print available data.
    search(keyword, ignore_case)
        Search for parameter.
    test_status()
        Shows the number of succeeded/failed tests.
    print_failed_tests()
        Print names and index of failed tests.
    print_subtest_results(nbr)
        Print subtest results for given test number.
    get_filename(nbr)
        Get filename from test number.
    get_data(parameter, include_hash)
        Get data for specified parameter.
    print_data(nbr)
        Print data for specified test number.
    get_yield(data, limit)
        Get yield for supplied data with the defined limit.
    print_testcase_details(nbr)
        Print testcase details.
    export_csv(targets, filename, delimiter)
        Export data to csv format, command line.
    export_gui(delimiter)
        Export to csv using GUI.
    draw_hist(parameter, title, range)
        Draw histogram.


    """
    def __init__(self):
        self.data = {}

    def __str__(self):
        pp = pprint.PrettyPrinter(indent=4)
        return pp.pformat(self.data)

    def print_filenames(self):
        """Print names of loaded files.

        """
        print("--filenames--")
        for name in self.filelist:
            print("  "+name)
        print("----------------")
        print(str(len(self.filelist))+" files.")

    def print_tests(self):
        """Print test names of loaded files.

        """
        print("--tests--")
        for test in self.tests:
            print("  "+test)

    def print_file_ext(self):
        """Print file extensions of loaded files.

        """
        print("--files--")
        for key, value in self.files.items():
            print("  "+key+":"+str(value))

    def available_data(self):
        """Print available data.

        """
        print("--available data--")
        for key in self.data.keys():
            print("  "+key)

    def search(self, keyword, ignore_case=True):
        """Search for parameter.

        Parameters
        ----------
        keyword : str
            The keyword to search for.
        ignore_case : bool
            True if uppercase and lowercase letters should be evaluated equally.

        Returns
        -------
        list
            List containing all found strings.
        """
        tmp = []
        for key in self.data.keys():
            if ignore_case:
                if re.search(keyword, key, re.IGNORECASE):
                    tmp.extend([key])
            else:
                if re.search(keyword, key):
                    tmp.extend([key])
        return tmp

    def test_status(self):
        """Shows the number of succeeded/failed tests.

        """
        success = 0
        fail = 0
        for value in self._meta['test_result']:
            if value[1] in ("PASS", "Pass", "pass", "Success", "SUCCESS"):
                success += 1
            else:
                fail += 1

        print("Test success:"+str(success)+", fail:"+str(fail))

    def print_failed_tests(self):
        """Print names and index of failed tests.

        """
        tmp = []
        for index, file in enumerate(self.filelist):
            if file.endswith(self.selected_ext):
                tmp.extend([file])

        for index, file in enumerate(tmp):
            res = ""
            if self.selected_ext == ".json":
                res = self._meta['test_result'][index][1]
            elif self.selected_ext == ".html":
                res = self._meta['test_result'][index][1]
            if res not in ("PASS", "Pass", "pass", "Success", "SUCCESS"):
                print("Test " + str([x[1] for x in self.hashes].index(file)) +
                      " \"" + file + "\" FAILED")

    def print_subtest_results(self, nbr):
        """ Print subtest results for given test number.

        """
        subtest_hash = self.hashes[nbr][0]
        print("Test nbr "+ str(nbr))
        if self.selected_ext == ".json":
            for key in self._meta['subtest_result'].keys():
                hashlist = [x[0] for x in self._meta['subtest_result'][key]]
                if subtest_hash in hashlist:
                    i = hashlist.index(subtest_hash)
                    print("   " + key + ": " + self._meta['subtest_result'][key][i][1])

        elif self.selected_ext == ".html":
            for key in self._meta['subtest_result'].keys():
                try:
                    hashlist = [x[0] for x in self._meta['subtest_result'][key]]
                    if subtest_hash in hashlist:
                        i = hashlist.index(subtest_hash)
                        print("   " + key + ": " + self._meta['subtest_result'][key][i][1])
                except IndexError:
                    pass #If there is no value, ignore.

    def get_filename(self, nbr):
        """Get filename from test number.

        Returns
        -------
        str
            The filename with number *nbr* or None.

        """
        return self.hashes[nbr][1]

    def get_data(self, parameter, include_hash=False):
        """ Get data for specified parameter.

        If *parameter* does not exist in the data the method tries to find
        similar parameters. This is handy in case of a typo or if the parameter
        name is long.

        Parameters
        ----------
        parameter : str
            The name of the data to extract.
        include_hash : bool
            returns list of tuples where the first argument is the test hash.
            This is needed for e.g. *get_yield*

        Returns
        -------
        list
            List containing the data associated with the supplied parameter
        """
        if parameter in self.data.keys():
            if isinstance(self.data[parameter][1], list):
                return self.data[parameter][1] if not include_hash else self.data[parameter]
            else:
                val = [x[1] for x in self.data[parameter]]
                return val if not include_hash else self.data[parameter]
        elif self.search(parameter):
            s = self.search(parameter)
            if s:
                for index, string in enumerate(s):
                    print("  " + str(index) + " " + string)
                selected_index = input("Did you mean any of the above? (0-" +
                                       str(len(s)-1) + "/n)")
                try:
                    if s[int(selected_index)]:
                        print(str(s[int(selected_index)]))
                        return self.get_data(str(s[int(selected_index)]),
                                             include_hash)
                except (ValueError, IndexError):
                    pass #if selected index is outside of list indices, do nothing
        else:
            print("Unknown parameter")

    def print_data(self, nbr):
        """ Print data for specified test number.

        """
        subtest_hash = self.hashes[nbr][0]
        for key in self.data.keys():
            hashes = [x[0] for x in self.data[key]]
            if subtest_hash in hashes:
                print("\"" + key + "\": " + str(self.data[key][hashes.index(subtest_hash)][1]))

    def get_yield(self, data, limit):
        """Get yield for supplied data with the defined limit.

        If *SensorId* is present in the parsed data then also calculate yield
        for unique sensor ids. Keep in mind that the yield is defined positive
        in the sense that the returned value correlates to the number of values
        greater than the limit. You may wish to invert it if you want the
        number of values lower than the limit.

        Parameters
        ----------
        data : list
            The data on which to calculate yield. For retest calculations
            please use *get_data* and set the *hash*-flag to True.
        limit : int
            Yield limit

        Returns
        -------
        tuple
            Tuple containing:
                y = calculated yield\n
                y_no_retest = calculated yield with unique sensor ids
        """
        if not data:
            print("Data not defined")
            return -1, -1
        if not isinstance(data[0], tuple):
            y = len(list(filter(lambda x: x > limit, data)))/len(data)
            return y, None

        y = len(list(filter(lambda x: x > limit, [x[1] for x in data])))/len(data)
        retest = []
        y_no_retest = -1
        try:
            ids = self.data['SensorId']
            seen = set()
            unique_ids = [item for item in ids if item[1] not in seen and not seen.add(item[1])]
            for index, dpoint in enumerate(data): #iterate data
                if data[index][0] in [x[0] for x in ids]: #if data has sensor id
                    if data[index][0] in [x[0] for x in unique_ids]: # if id has not been found
                        dindex = [x[0] for x in self._meta['test_result']].index(data[index][0])
                        res = self._meta['test_result'][dindex][1]
                        if  res == "Success" or res == "PASS": #only add if test succeeded
                            uindex = [x[0] for x in unique_ids].index(data[index][0])
                            del unique_ids[uindex] #mark as found
                            retest.extend([dpoint])
                    else:
                        pass
                else:
                    retest.extend([dpoint])
            y_no_retest = len(list(filter(lambda x: x > limit, [x[1] for x in retest])))/len(retest)

        except KeyError:
            warnings.warn("Sensor ID not available. Cannot calculate 'yield_no_retest'.",
                          RuntimeWarning, 2)
        return y, y_no_retest

    def print_testcase_details(self, nbr):
        """Print testcase details.

        Parameters
        ----------
        nbr : int
            Test number on which to operate.

        """
        print("--testcase details--")
        test_hash = self.hashes[nbr][0]
        for key in self.data.keys():
            if test_hash in [x[0] for x in self.data[key]]:
                i = [x[0] for x in self.data[key]].index(test_hash)
                print("   " + key + ": " + str(self.data[key][i][1]))

    def export_csv(self, targets=None, filename="output.csv", delimiter=";"):
        """Export data to csv format, command line.

        Specify your data in a list and have it printed in a csv-file.
        For a more user-friendly GUI version, use export_gui() method.

        Parameters
        ----------
        targets : list
            Parameters selected for export.
        filename : str
            Name of output file.
        delimiter : str
            Column separation character.

        """
        if not self.data:
            raise Exception("No data to export")

        with open(filename, 'w') as handle:
            nbr_of_files = int(self.files[self.selected_ext])
            header = ""
            if targets:
                header += delimiter.join(targets) + delimiter
            else:
                for key in self.data.keys(): #combine header
                    if ":Registers" not in key:
                        header += key+delimiter
            handle.write(header+"\n")

            for k in range(nbr_of_files): #iterate over files
                tmp = ""
                if targets:
                    for index, target in enumerate(targets):
                        try:
                            tmp += str(self.data[target][k][1])
                            tmp += "\n" if index == len(targets)-1 else delimiter
                        except IndexError:
                            pass
                else:
                    for index, key in enumerate(self.data.keys()): #iterate over keys
                        try:
                            if ":Registers" not in key:
                                tmp += str(self.data[key][k][1])
                                tmp += "\n" if index == len(self.data.keys())-1 else delimiter
                        except IndexError:
                            tmp += "\n" if index == len(self.data.keys())-1 else delimiter
                handle.write(tmp)

    def draw_hist(self, parameter, title, range_=[]):
        """Draw histogram.

        Uses get_data function to extract data, which also means it will
        provide corrections if the provided parameter does not exist or if it
        is misspelled.

        Parameters
        ----------
        parameter : str
            The parameter to get data from.
        title : str
            Histogram title.
        range_ : list
            Start and end points of x-range

        """
        data = self.get_data(parameter)
        y,yk = hist.create(data)
        if range_:
            hist.plot(y, yk, parameter, title, scale=1, range_=range_)
        else:
            hist.plot(y, yk, parameter, title, scale=3)

    def export_gui(self, delimiter=";"):
        """ Export to csv using GUI.

        Uses a GUI for data selection. For list-specific data selection use
        export_csv() method.

        Parameters
        ----------
        delimiter : str
            Column separation character.

        """
        master = Tk() #root widget

        def export():
            tmp = []
            indices = listbox.curselection()
            if not indices:
                messagebox.showwarning("Warning", "No data selected.")
                return
            for i in indices:
                tmp.append(listbox.get(i))
            filename=e1.get()
            self.export_csv(targets=tmp, filename=filename, delimiter=delimiter)
            path_to_csv = "/".join(os.path.realpath(__file__).split("/")[:-2])
            print("Data exported to: " + path_to_csv + "/" + filename)
            master.destroy()

        def select_all():
            listbox.select_set(0, END)

        def unselect_all():
            listbox.selection_clear(0, END)

        l1 = Label(master, font=("Helvetica", 16), height=3, text="Select the parameters you wish to export.")
        l1.grid(row=0, columnspan=4)
        listbox = Listbox(master, selectmode=MULTIPLE, width=60, height=40, font=("Arial", 9))
        listbox.grid(row=1, columnspan=4)
        for item in self.data.keys():
            listbox.insert(END, item)

        l2 = Label(master, text="Filename", font=("Arial",15))
        l2.grid(row=2, column=0)
        e1 = Entry(master)
        e1.grid(row=2, column=1, columnspan=3)
        e1.insert(0, "output.csv")
        b1 = Button(master, text="Select all", command=select_all, font=("Arial",15))
        b1.grid(row=3, column=0)
        b2 = Button(master, text="Unselect all", command=unselect_all, font=("Arial",15))
        b2.grid(row=3, column=1)
        b3 = Button(master, text='Export and quit', command=export, font=("Arial",15))
        b3.grid(row=3, column=3)


        master.mainloop()


class NotInitializedError(Exception):
    pass

class UnsupportedFileFormatError(Exception):
    pass

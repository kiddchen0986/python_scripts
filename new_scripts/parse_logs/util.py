import fnmatch
import os
import re
from functools import wraps
from win32api import GetSystemMetrics
import shutil

def gen_find(log_pattern:str, log_path:str):
    for path, _, file_list in os.walk(log_path):
        for name in fnmatch.filter(file_list, log_pattern):
            yield os.path.join(path, name)

def CreateFolder(file):
    if(not os.path.exists(file)):
        os.mkdir(file)
    else:
        shutil.rmtree(file)
        os.makedirs(file)

def optional_debug(func):
    @wraps(func)
    def wrapper(*args, debug=False, **kwargs):
        if debug:
            print('Debugging {} {} {}\n'.format(func.__qualname__, args, kwargs))

        return func(*args, **kwargs)
    return wrapper

def format_ofilm_json(path):
    """
    Used to format ofilm's incorrect jsons to correct format
    """
    output = gen_find('*.json', path)
    for file in output:
        log_name = file.split('.json')[0]
        with open(file, mode='r', encoding='utf-8') as f:
            text = f.read()

            res = re.findall('}\n{', text)
            new_text = text.replace('}\n{', '},\n{', len(res))
            #print(new_text)

            new_text = '{\n"TestReportItems": [\n' + new_text + ']\n}'
            with open(log_name + '_changed.json', mode='w', encoding='utf-8') as wf:
                wf.write(new_text)

def split_truly_json(path):
    """
    Used to split merged txt & json logs from truly
    """
    files = gen_find('*_log.txt', path)
    for file in files:
        log_name = file.split('__log.txt')[0]
        print('spliting', file)
        with open(file, mode='r', encoding='utf-8') as rf:
            text_lines = rf.readlines()
            json_start_index = 0
            for i, line in enumerate(text_lines):
                if line.startswith('{'):
                    json_start_index = i
                    break

            with open(log_name + '_result.json', mode='w', encoding='utf-8') as wf:
                wf.writelines(text_lines[json_start_index:-2])


class Typed:
    def __init__(self, name, expected_type):
        self.name = name
        self.expected_type = expected_type


    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if not isinstance(value, self.expected_type):
            raise TypeError('Expected ' + str(self.expected_type))
        instance.__dict__[self.name] = value

    def __delete__(self, instance):
        del instance.__dict__[self.name]


def typeassert(**kwargs):
    def decorate(cls):
        for name, expected_type in kwargs.items():
            setattr(cls, name, Typed(name, expected_type))
        return cls
    return decorate


def get_window_size():
    return (GetSystemMetrics(0) / 100, GetSystemMetrics(1) / 100)


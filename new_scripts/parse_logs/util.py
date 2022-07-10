import os
import fnmatch
import time

def gen_find(filepat, top):
    for path, _, file_list in os.walk(top):
        for name in fnmatch.filter(file_list, filepat):
            yield os.path.join(path, name)

def log_time(method):

    def timed(*args, **kwargs):
        ts = time.time()
        result = method(*args, **kwargs)
        te = time.time()

        print('%r (%r, %r) %2.2f sec' % (method.__name__, args, kwargs, te - ts))

        return result

    return timed
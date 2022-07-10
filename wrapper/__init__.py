"""contains checked in binary libraries as well as wrapped libraries

Here we find wrapped .dll libraries as well as copies of binary libraries. Each .dll file receives its separate
folder containing one .py file for each .h or .c file with the same filename. This is to facilitate the
updating of a wrapped library when an original .dll file is modified. The wrapping in this repository is built
on the built-in package in python ctypes; a versatile python-to-c API.
"""

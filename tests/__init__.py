"""contains tests that build on native tests in .dll's

This is where new tests may be added that build on binary libraries; tests that are a series of native
tests from a wrapped library. The tests found in this package use the functions found in
wrapper.run_native_test, which in turn use the wrapped functions found in the sub-directories of wrapper
(eg. wrapper.prodtestlib). These tests perform tests when provided with certain arguments; logged image
files(i.e. Checkerboard.png), product_type etc."""
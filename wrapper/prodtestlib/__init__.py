"""wraps prodtestlib.dll

Contains the layer closest to the actual native tests found in prodtestlib.dll. It creates and handles the
necessary python translated structs (such as CheckerboarResult & CheckerboardConfig which are
“translations” of fpc_checkerboard_result_t and fpc_checkerboard_config_t).
"""

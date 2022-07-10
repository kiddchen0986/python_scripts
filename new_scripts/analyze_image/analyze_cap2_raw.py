import numpy as np
import ctypes
import sys
import matplotlib.pyplot as plt

def analyze_cap2(path, w, h, show_img = False):
    capacitance_float = np.fromfile(path, dtype=ctypes.c_float)
    capacitance_float_sorted = sorted(capacitance_float)
    print('Min =', capacitance_float_sorted[0])
    min5 = capacitance_float_sorted[len(capacitance_float_sorted) // 20]
    print('Min5 =', min5)
    max5 = capacitance_float_sorted[len(capacitance_float_sorted) - len(capacitance_float_sorted) // 20]
    print('Max5 =', max5)
    print('Max =', capacitance_float_sorted[len(capacitance_float_sorted) - 1])

    median = capacitance_float_sorted[len(capacitance_float_sorted) // 2]
    print('Median =', median)
    print('Signal Strength =', median)

    uniformity = (max5 - min5) / capacitance_float_sorted[len(capacitance_float_sorted) // 2]
    print('uniformity_level =', uniformity)

    if show_img:
        plt.imshow(capacitance_float.reshape(h, w), cmap='gray')
        plt.show()

    return median, uniformity

if __name__ == '__main__':
    try:
        analyze_cap2(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
    except IndexError as e:
        print('python analyze_cap2_raw.py <raw_path> <width> <height>')
    except Exception as e:
        print(e)





"""Tools for creating histograms of data"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from utils.utils_common import create_file_path

INTERVAL_SIZE = 60

result_keys = ["result", "capacitance_result", "blob_result"]


def create_from_test_seq_packs(test_seq_packs, scale=0, combine_figs=True):
    """Creates histograms from the data in the test_seq_packs

    IMPORTANT: To know how to interpret the data found in the test_seq_packs it is required that the 'result' attribute
    in the test_packages have the 'histogram' dict containing the information.

    :param test_seq_packs: list of test_sequence_packages
    :type test_seq_packs: list of dicts
    :param scale: If 0: scale 0-255. If 1: use provided range if not None ("range", found in histogram). \
    If 2: ±INTERVAL_SIZE/2 around the maximum value. If 3: automatic scaling.
    :type scale: int
    :param combine_figs: If True, combine histograms for other attributes in the same figure. Knows which histograms \
    to combine through the 'histogram' dict in the 'result' attribute.
    :type combine_figs: bool
    :return: list of file_paths to the histograms
    :rtype: list of str
    """
    histograms = {}
    test_sequence_name = test_seq_packs[0]["test_sequence"]

    for tp in test_seq_packs[0]["test_packages"]:
        # Loop through the test_packages of the first test sequence

        # Retrieve the histogram dict from the result struct (containing the attributes that are interesting to create
        # histogram of
        keys = sorted(list(tp))
        for key in keys:
            if key in result_keys:

                if tp["test_name"] in histograms:
                    histograms[tp["test_name"]][key] = tp[key].histogram
                else:
                    histograms[tp["test_name"]] = {key: tp[key].histogram}

        for _, struct in histograms[tp["test_name"]].items():
            for _, histogram in struct.items():
                # Loop all the attributes in the histogram dict (from the result struct)
                # Add a collective array for all the values of that attribute
                histogram["data"] = []

    # Collect all the data for each attribute which a histogram will be created for
    for test_seq in test_seq_packs:
        # Loop through the test_sequence_packages
        if len(test_seq["error_code"]) is 0:
            # Ignore this test_sequence if there was error in the test
            for tp in test_seq["test_packages"]:
                # Loop through the test_packages of the test_sequence_package

                for struct_name, struct in histograms[tp["test_name"]].items():
                    for attr, histogram in struct.items():
                        # Loop through the relevant attributes of the native test
                        # Retrieve the attribute value from the current native test and add it to the collective array
                        histogram["data"].append(getattr(tp[struct_name], attr))

    fps = []

    # Create the histograms
    for test_name, structs in histograms.items():
        # Loop through the combined native tests

        # Keep track of which histograms have been plotted for each native test. This is to avoid dual plotting, when
        # the combine_figs is True
        plotted_attrs = []

        for struct, attributes in structs.items():
            for attr, histogram in attributes.items():
                # Loop through attributes for each native test

                if attr in plotted_attrs:
                    # Skip this histogram if it has already been plotted
                    continue

                if len(histogram["data"]) is 0:
                    # If there is no data (if there were continuous errors and data was not collected),
                    # skip this attribute
                    continue

                hist, bins = create(histogram["data"])
                histogram["hist"] = hist
                histogram["bins"] = bins
                histogram["scale"] = scale
                to_plot_same_fig = {attr: histogram}

                if combine_figs and histogram["combine_figs"]:
                    # If relevant histograms are to be put in the same figure
                    attr = histogram["combine_figs_name"]

                    for other_hist in histogram["combine_figs"]:
                        hist, bins = create(attributes[other_hist]["data"])
                        attributes[other_hist]["hist"] = hist
                        attributes[other_hist]["bins"] = bins
                        attributes[other_hist]["scale"] = scale

                        to_plot_same_fig[other_hist] = attributes[other_hist]

                title = "{}_{}_{}_{}".format(test_sequence_name, test_name, attr, "histogram")

                new_figure = True
                for name, vals in to_plot_same_fig.items():
                    # Plot the histogram/s
                    fig = plot(vals["hist"],
                               vals["bins"],
                               name,
                               title,
                               vals["min"],
                               vals["max"],
                               vals["scale"],
                               new_figure,
                               vals["range"])

                    plotted_attrs.append(name)
                    new_figure = False

                # Save the figure
                fps.append(write(fig, title))
    return fps


def get_amount_outside_interval(amounts, values, min_, max_):
    """Calculates how many values are outside the range decided by min\_ and max\_

    :param amounts: array containing how many instances of each value
    :type amounts: an array of int
    :param values: array of values
    :type values: an array of int
    :param min\_: the minimum value
    :type min\_: int
    :param max\_: the maximum value
    :type max\_: int
    :return: (amount under, amount over)
    """
    under, over = 0, 0

    for i, val in enumerate(values):
        if val < min_:
            under += amounts[i]
        elif val > max_:
            over += amounts[i]

    return under, over


def create(array):
    """Create a histogram from an array of data

    :param array:
    :return: the values of the histogram and the bin_edges
    :rtype: (array, array)
    """
    unique_values = np.unique(array)
    # The rightmost bin_edge value needs to be added also
    bin_edges = np.append(unique_values, unique_values[-1] + 1)
    hist = np.histogram(array, bin_edges)
    return hist


def plot(hist, bins, data_set_name, title,
         text=None, min_=None, max_=None,
         scale=0, new_figure=True, range_=None,
         show=False):
    """Plot the histogram array (and show it)

    :param hist: the values of the histogram (occurrences of each bin)
    :type hist: ndarray
    :param bins: defines the edges of the equal-width bin wherein
    :type bins: ndarray
    :param data_set_name: name of specific data_set_name
    :type data_set_name: str
    :param title: plot title
    :type title: str
    :param text: an extra text box of information
    :type text: str
    :param min_: the parameter min value
    :type min_: number
    :param max_: the parameter max value
    :type max_: number
    :param scale: If 0: scale 0-255. If 1: use provided range\_ if not None. If 2: ±INTERVAL_SIZE/2 around the \
    maximum value. If 3: automatic scaling.
    :type scale: int
    :param new_figure: If true, the plot is put in a new figure
    :type new_figure: bool
    :param range\_: the x-range
    :type range\_: 2-element list
    :param show: whether the plot is to be shown or not
    :type show: bool
    :return: the figure
    :rtype: matplotlib.pyplot.figure
    """
    if new_figure:
        # If a new figure is wanted, the previous is cleared
        plt.cla()
        plt.clf()
        plt.close()

        items, labels = [], []

    else:
        items, labels = plt.gca().get_legend_handles_labels()

    plt.figure(1)

    if len(bins) > 2:
        bins = bins[:-1]
        bin_size = bins[1] - bins[0]
    else:
        # If there is only '1' bin
        bin_size = bins[1] - bins[0]
        bins = bins[:-1]

    items.append(plt.bar(bins, hist, 0.9*bin_size, label=data_set_name))
    labels.append(data_set_name)

    if min_ is not None:
        # If a min value is provided, a line is drawn at this point
        plt.axvline(x=(min_-0.5), color='r')
    if max_ is not None:
        # If a max value is provided, a line is drawn at this point
        plt.axvline(x=(max_-0.5), color='r')

    plt.title(title)
    axes = plt.gca()

    if scale is 0:
        # Fixed scale between [0, 255]
        axes.set_xbound([0, 255])

    elif scale is 1:
        # If range_ is a list of length 2, use this range. Else use [0,255]
        if range_ is not None:
            if len(range_) is 2:
                axes.set_xbound(range_)

    elif scale is 2:
        # Scale of size INTERVAL_SIZE, if possible with center around maximum value
        # NOTE: this will be very non-effective for combined figs as it changes the range for the latest histogram
        most_freq_val = bins[np.argmax(hist)]
        low = most_freq_val - INTERVAL_SIZE/2
        high = most_freq_val + INTERVAL_SIZE/2

        if low < 0:
            # If low is less than 0, take the difference and add it to high instead
            high += abs(low)
            low = 0
        elif high > 255:
            # If hih is bigger than 255, take the difference and subtract it from low instead
            low -= high-255
            high = 255

        axes.set_xbound([low, high])

    else:
        # Automatic scaling
        pass

    # Following code can be used if one wishes to add the number of pixels outsie of the range to the histogram
    # if min_ is not None and max_ is not None:
    #     under, over = get_amount_outside_interval(hist, bins, min_, max_)
    #
    #     lbl = "{}\n# of values: {}\n# under limit: {}\n# over limit: {}".format(data_set_name, sum(hist), under, over)
    #     items.append(Rectangle((0, 0), 1, 1, fc="w", fill=False, edgecolor="none", linewidth=0, label=lbl))
    #     labels.append(lbl)
    #
    #     axes.add_patch(items[-1])

    plt.legend(items, labels)

    if text:
        plt.gca().text(0.95, 0.05, text, ha='right', va='center', transform=plt.gca().transAxes, bbox={'alpha': 0.5,
                                                                                                    'pad': 10})

    if show:
        plt.show()

    return plt.figure(1)


def write(fig, title):
    """Save the histogram plot to a file

    :param fig: the figure to be written
    :type fig: matplotlib.pyplot.figure
    :param title: plot title
    :type title: str
    :return: file_path
    :rtype: str
    """
    file_path = create_file_path(title, ".png")
    fig.savefig(file_path, bbox_inches='tight')

    return file_path

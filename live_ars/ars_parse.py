#!/usr/bin/env python

from toopazo_tools.matplotlib import FigureTools, PlotTools, plt
from toopazo_tools.file_folder import FileFolderTools
from toopazo_tools.time_series import TimeseriesTools as TSTools
from toopazo_tools.data2d import Data2D
from toopazo_ulg.parse_file import UlgParser
from toopazo_ulg.plot_main import UlgPlot as UlgMain

from ars_dec22_data import ArsDec22Data

import pandas
import numpy as np
import operator
from scipy import stats
import csv
import argparse
import pickle
# import time
# import serial
# import pprint
# import io
# import signal
# import sys
import warnings
import matplotlib
matplotlib.rcParams.update({'font.size': 14})


class ArsParser:
    def __init__(self):
        pass

    @staticmethod
    def get_pandas_dataframe(ars_file):
        ars_df = pandas.read_csv(ars_file, skipinitialspace=True)
        return ars_df

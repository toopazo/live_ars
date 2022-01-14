#!/usr/bin/env python

import pandas


class ArsParser:
    def __init__(self):
        pass

    @staticmethod
    def get_pandas_dataframe(ars_file):
        ars_df = pandas.read_csv(ars_file, skipinitialspace=True)
        return ars_df

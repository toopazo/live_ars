#!/usr/bin/python3

import sys
import matplotlib
import pandas
import matplotlib.pyplot as plt
import numpy as np
from toopazo_tools.file_folder import FileFolderTools as FFTools


class PlotTelemetryLog:
    """
    Class to plot data from log
    """

    def __init__(self, filepath, index_col):
        self.file_path = filepath
        [head, tail] = FFTools.get_file_split(filepath)
        self.file_folder = head
        self.file_name = tail
        [root, ext] = FFTools.get_file_splitext(filepath)
        _ = root
        self.file_extension = ext

        self.dataframe = pandas.read_csv(
            self.file_path, index_col=index_col, parse_dates=True)
        # self.dataframe.set_index(
        #     index_col, inplace=True, verify_integrity=True)
        # print(self.dataframe)
        # print(self.dataframe.shape)
        # print(self.dataframe.columns)
        # print(self.dataframe.iterrows())

        matplotlib.use('Qt5Agg')

    def save_current_plot(self, tag_arr, sep, ext):
        assert isinstance(self.file_name, str)
        name = self.file_name.replace(self.file_extension, "")
        for tag in tag_arr:
            name = name + sep + str(tag)
        file_path = self.file_folder + '/' + name + ext

        # plt.show()
        plt.savefig(file_path)
        # return file_path

    def plot_dataframe(self, dataframe):
        tfigsize = (12, 6)
        # fig, axs = plt.subplots(figsize=tfigsize)
        # df.plot()
        # df.plot.area(ax=axs, subplots=True)
        dataframe.plot(figsize=tfigsize, subplots=True)

        # cmap = ListedColormap(['#0343df', '#e50000', '#ffff14', '#929591'])
        # ax = df.plot.bar(x='year', colormap=cmap)
        # ax.set_xlabel(None)
        # ax.set_ylabel('Seats')
        # ax.set_title('UK election results')


def calibrate_dataframe(dataframe, col_curi, col_rpmi):
    assert isinstance(dataframe, pandas.DataFrame)

    frq_arr = dataframe[col_rpmi].values
    cur_arr = dataframe[col_curi].values
    print(frq_arr)
    print(cur_arr)

    # 1) Divide samples into 0rpm and non0rpm
    dataframe_0rpm = dataframe[dataframe[frq_arr] == 0]
    dataframe_non0rpm = dataframe[dataframe[frq_arr] != 0]

    for sample in range(0, nsamples):
        time = sample
        rpm = frq_arr[sample] * 60      # Hz to RPM
        rpm = ArsParser.apply_linreg(rpm)
        cur = cur_arr[sample]

        # Add entire (time, rpm, cur) to caldata
        if ktime in caldata:
            caldata[ktime].append(time)
            caldata[krpm].append(rpm)
            caldata[kcur].append(cur)
        elif ktime not in caldata:
            caldata[ktime] = [time]
            caldata[krpm] = [rpm]
            caldata[kcur] = [cur]

        # Add 0rpm (time, rpm, cur) to caldata
        if (rpm == 0) and (ktime_0rpm in caldata):
            caldata[ktime_0rpm].append(time)
            caldata[krpm_0rpm].append(rpm)
            caldata[kcur_0rpm].append(cur)
        elif (rpm == 0) and (ktime_0rpm not in caldata):
            caldata[ktime_0rpm] = [time]
            caldata[krpm_0rpm] = [rpm]
            caldata[kcur_0rpm] = [cur]

        # Add non0rpm (time, rpm, cur) to caldata
        if (rpm != 0) and (ktime_non0rpm in caldata):
            caldata[ktime_non0rpm].append(time)
            caldata[krpm_non0rpm].append(rpm)
            caldata[kcur_non0rpm].append(cur)
        elif (rpm != 0) and (ktime_non0rpm not in caldata):
            caldata[ktime_non0rpm] = [time]
            caldata[krpm_non0rpm] = [rpm]
            caldata[kcur_non0rpm] = [cur]

        # 2) Change the current scale
        # According to
        # https://www.sparkfun.com/datasheets/BreakoutBoards/0712.pdf
        # The ACS712ELCTR-20A sensor maps current and voltage as
        # [-20A +20A] <=> [0.5V 4.5V]
        # This gets mapped by the Arduino ADC as
        # [0V 5V] <=> [0 1023]
        # 5 volts / 1024 units = 0.0049 volts (4.9 mV) per unit
        try:
            arduino_sensitivity = 5 / 1024      # V/count
            acs712_sensitivity = 100 / 1000     # V/A
            volt_zero_cur = 2.5

            counts = np.array(caldata[kcur])
            voltage = counts * arduino_sensitivity
            current = (voltage - volt_zero_cur) / acs712_sensitivity
            caldata[kcur] = current

            counts = np.array(caldata[kcur_0rpm])
            voltage = counts * arduino_sensitivity
            current = (voltage - volt_zero_cur) / acs712_sensitivity
            caldata[kcur_0rpm] = current

            counts = np.array(caldata[kcur_non0rpm])
            voltage = counts * arduino_sensitivity
            current = (voltage - volt_zero_cur) / acs712_sensitivity
            caldata[kcur_non0rpm] = current
        except KeyError:
            # This channel was always at 0rpm or always non0rpm
            pass

        # 3) Subtract from kcur_non0rpm the average current of 0rpm
        try:
            cur_0rpm_avg = np.mean(caldata[kcur_0rpm])
            cur_non0rpm = caldata[kcur_non0rpm]
            caldata[kcur_non0rpm] = cur_non0rpm - cur_0rpm_avg
            cur_0rpm = caldata[kcur_0rpm]
            caldata[kcur_0rpm] = cur_0rpm - cur_0rpm_avg
        except KeyError:
            # This channel was always at 0rpm or always non0rpm
            pass

        try:
            print('[calibrate_rawdata] channel %s has %s 0rpm samples'
                  % (nchan, len(caldata[ktime_0rpm])))
            print('[calibrate_rawdata] channel %s has %s non0rpm samples'
                  % (nchan, len(caldata[ktime_non0rpm])))
        except KeyError:
            # This channel was always at 0rpm or always non0rpm
            pass
    # # debug
    # caldata = rawdata
    # print('[calibrate_rawdata] caldata.keys() %s'
    #       % caldata.keys())
    return dataframe


def parse_user_arg(filename):
    filename = FFTools.full_path(filename)
    print('target file {}'.format(filename))
    if FFTools.is_file(filename):
        cwd = FFTools.get_cwd()
        print('current folder {}'.format(cwd))
    else:
        arg = '{} is not a file'.format(filename)
        raise RuntimeError(arg)
    return filename


if __name__ == '__main__':
    ufilename = sys.argv[1]
    ufilename = parse_user_arg(ufilename)
    uindexcol = sys.argv[2]

    # Header of kdecan log file log_1_2021-09-16-19-05-59.kdecan
    #     time s, escid, voltage V, current A, angVel rpm, temp degC,
    #     warning, inthtl us, outthtl perc

    col_sps = "sps"
    col_mills = " mills"
    col_sesc = " secs"
    col_dtmills = " dtmills"
    col_cur1 = " cur1"
    col_cur2 = " cur2"
    col_cur3 = " cur3"
    col_cur4 = " cur4"
    col_cur5 = " cur5"
    col_cur6 = " cur6"
    col_cur7 = " cur7"
    col_cur8 = " cur8"
    col_rpm1 = " rpm1"
    col_rpm2 = " rpm2"
    col_rpm3 = " rpm3"
    col_rpm4 = " rpm4"
    col_rpm5 = " rpm5"
    col_rpm6 = " rpm6"
    col_rpm7 = " rpm7"
    col_rpm8 = " rpm8"

    plotlog = PlotTelemetryLog(ufilename, uindexcol)
    udataframe = plotlog.dataframe
    udataframe = calibrate_dataframe(udataframe, col_cur8, col_rpm8)

    # plotlog = PlotTelemetryLog(ufilename, uindexcol)
    # for escid in range(11, 19):
    #     udataframe = plotlog.dataframe
    #     # udataframe = udataframe[udataframe[col_escid] == escid]
    #     col_curi = " cur{}".format(escid-10)
    #     col_rpmi = " rpm{}".format(escid - 10)
    #     col_arr = [col_sps, col_curi, col_rpmi]
    #     udataframe = udataframe[col_arr]
    #     udataframe = calibrate_dataframe(udataframe, col_curi, col_rpmi)
    #     plotlog.plot_dataframe(udataframe)
    #     plotlog.save_current_plot(
    #         tag_arr=["escid{}".format(escid)], sep="_", ext='.png')

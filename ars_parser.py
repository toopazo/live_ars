#!/usr/bin/env python

from toopazo_tools.matplotlib import FigureTools, PlotTools, plt
from toopazo_tools.file_folder import FileFolderTools
from toopazo_tools.time_series import TimeseriesTools
from toopazo_ulg.file_parser import UlgParser
from toopazo_ulg.plot_main import UlgMain

from ars_dec22_data import ArsDec22Data

import numpy as np
from scipy import stats
import csv
import argparse
import pickle
import time
# import serial
# import pprint
# import io
# import signal
# import sys
import matplotlib
matplotlib.rcParams.update({'font.size': 14})


class ArsParser:
    def __init__(self, bdir, arsfile, ulgfile, verbose):
        # bdir = FileFolderTools.full_path(user_args.bdir)
        self.bdir = bdir
        self.logdir = bdir + '/logs'
        self.tmpdir = bdir + '/tmp'
        self.plotdir = bdir + '/plots'

        if FileFolderTools.is_file(arsfile):
            self.arsfile = arsfile
            basename = FileFolderTools.get_file_basename(self.arsfile)
            self.arsfile_basename = basename.replace('.ars', '')
        else:
            # raise RuntimeError
            arg = '[__init__] No such file arsfile %s' % arsfile
            print(arg)
            return

        if FileFolderTools.is_file(ulgfile):
            self.ulgfile = ulgfile
            basename = FileFolderTools.get_file_basename(self.ulgfile)
            self.ulgfile_basename = basename.replace('.ulg', '')
            self.ulgmain = UlgMain(self.bdir)
            self.ulgmain.check_ulog2csv(ulgfile)
        else:
            self.ulgfile = ''
            self.ulgfile_basename = ''
            self.ulgmain = None

        arg = '[__init__] arsfile %s' % self.arsfile
        print(arg)
        arg = '[__init__] ulgfile %s' % self.ulgfile
        print(arg)

        self.nsamples = 0
        self.nchannels = 0
        self.rawdata = None
        self.caldata = None
        self.windata = None
        self.syndata = None

        self.channel_arr = None
        self.motor_arr = None
        self.motor_pairs = None

        self.verbose = verbose
        self.load_data()

    def load_data(self):
        self.rawdata = self.parse_file()
        self.caldata = self.calibrate_rawdata()
        window = 4  # time window for data averaging
        self.windata = self.calculate_windata(window)

        self.channel_arr = list(range(0, self.nchannels))
        # self.channel_arr = [0, 1, 2, 3, 4, 5, 6, 7]
        self.motor_arr = [3, 8, 4, 7, 0, 0, 0, 0]
        self.motor_pairs = [(3, 8), (4, 7)]     # , (0, 0), (0, 0)]

        for nchan in range(0, self.nchannels):
            motor = self.channel_to_motor(nchan)
            if self.verbose:
                arg = '[load_data] nchan ' + str(nchan) + ', m3_motor ' + \
                      str(motor)
                print(arg)
        for motor in self.motor_arr:
            nchan = self.motor_to_channel(motor)
            if self.verbose:
                arg = '[load_data] m3_motor ' + str(motor) + ', nchan ' + \
                      str(nchan)
                print(arg)

    def plot(self):
        # pltdata = self.rawdata
        # pltdata = self.caldata
        pltdata = self.windata

        self.plot_motors(pltdata)
        self.plot_arms(pltdata)

        ulgfile = self.ulgfile
        if FileFolderTools.is_file(ulgfile):
            # ulgmain.process_file(ulgfile)
            closefig = True
            self.ulgmain.ulg_plot_mixer.mixer_input_output(ulgfile, closefig)
            self.ulgmain.ulg_plot_mixer.actuator_controls_0_0(ulgfile, closefig)
            self.ulgmain.ulg_plot_mixer.actuator_outputs_0(ulgfile, closefig)

    def parse_file(self):
        self.rawdata = {}
        with open(self.arsfile) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            self.nsamples = 0

            for row in csv_reader:
                if self.nsamples == 0:
                    self.nchannels = int(len(row)/2)

                for nchan in range(0, self.nchannels):
                    ktime = 'time%s' % nchan
                    key_frq = 'frq%s' % nchan
                    kcur = 'cur%s' % nchan

                    time = self.nsamples
                    frq = int(row[0 + nchan])
                    cur = int(row[8 + nchan])

                    # Add entire (time, rpm, cur) to rawdata
                    if ktime in self.rawdata:
                        self.rawdata[ktime].append(time)
                        self.rawdata[key_frq].append(frq)
                        self.rawdata[kcur].append(cur)
                    elif ktime not in self.rawdata:
                        self.rawdata[ktime] = [time]
                        self.rawdata[key_frq] = [frq]
                        self.rawdata[kcur] = [cur]
                # Get ready for next row
                self.nsamples += 1

        print('[parse_file] nchannels %s' % self.nchannels)
        print('[parse_file] nsamples %s' % self.nsamples)
        return self.rawdata

    def calibrate_rawdata(self):
        self.caldata = {}
        for nchan in range(0, self.nchannels):
            key_frq = 'frq%s' % nchan
            kcur = 'cur%s' % nchan
            frq_arr = self.rawdata[key_frq]
            cur_arr = self.rawdata[kcur]

            # 1) Divide samples into 0rpm and non0rpm
            [ktime, krpm, kcur] = \
                ArsParser.data_keys(nchan, '')
            [ktime_0rpm, krpm_0rpm, kcur_0rpm] = \
                ArsParser.data_keys(nchan, '0rpm')
            [ktime_non0rpm, krpm_non0rpm, kcur_non0rpm] = \
                ArsParser.data_keys(nchan, 'non0rpm')

            for sample in range(0, self.nsamples):
                time = sample
                rpm = frq_arr[sample] * 60      # Hz to RPM
                rpm = ArsParser.apply_linreg(rpm)
                cur = cur_arr[sample]

                # Add entire (time, rpm, cur) to caldata
                if ktime in self.caldata:
                    self.caldata[ktime].append(time)
                    self.caldata[krpm].append(rpm)
                    self.caldata[kcur].append(cur)
                elif ktime not in self.caldata:
                    self.caldata[ktime] = [time]
                    self.caldata[krpm] = [rpm]
                    self.caldata[kcur] = [cur]

                # Add 0rpm (time, rpm, cur) to caldata
                if (rpm == 0) and (ktime_0rpm in self.caldata):
                    self.caldata[ktime_0rpm].append(time)
                    self.caldata[krpm_0rpm].append(rpm)
                    self.caldata[kcur_0rpm].append(cur)
                elif (rpm == 0) and (ktime_0rpm not in self.caldata):
                    self.caldata[ktime_0rpm] = [time]
                    self.caldata[krpm_0rpm] = [rpm]
                    self.caldata[kcur_0rpm] = [cur]

                # Add non0rpm (time, rpm, cur) to caldata
                if (rpm != 0) and (ktime_non0rpm in self.caldata):
                    self.caldata[ktime_non0rpm].append(time)
                    self.caldata[krpm_non0rpm].append(rpm)
                    self.caldata[kcur_non0rpm].append(cur)
                elif (rpm != 0) and (ktime_non0rpm not in self.caldata):
                    self.caldata[ktime_non0rpm] = [time]
                    self.caldata[krpm_non0rpm] = [rpm]
                    self.caldata[kcur_non0rpm] = [cur]

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

                counts = np.array(self.caldata[kcur])
                voltage = counts * arduino_sensitivity
                current = (voltage - volt_zero_cur) / acs712_sensitivity
                self.caldata[kcur] = current

                counts = np.array(self.caldata[kcur_0rpm])
                voltage = counts * arduino_sensitivity
                current = (voltage - volt_zero_cur) / acs712_sensitivity
                self.caldata[kcur_0rpm] = current

                counts = np.array(self.caldata[kcur_non0rpm])
                voltage = counts * arduino_sensitivity
                current = (voltage - volt_zero_cur) / acs712_sensitivity
                self.caldata[kcur_non0rpm] = current
            except KeyError:
                # This channel was always at 0rpm or always non0rpm
                pass

            # 3) Subtract from kcur_non0rpm the average current of 0rpm
            try:
                cur_0rpm_avg = np.mean(self.caldata[kcur_0rpm])
                cur_non0rpm = self.caldata[kcur_non0rpm]
                self.caldata[kcur_non0rpm] = cur_non0rpm - cur_0rpm_avg
                cur_0rpm = self.caldata[kcur_0rpm]
                self.caldata[kcur_0rpm] = cur_0rpm - cur_0rpm_avg
            except KeyError:
                # This channel was always at 0rpm or always non0rpm
                pass

            try:
                print('[calibrate_rawdata] channel %s has %s 0rpm samples'
                      % (nchan, len(self.caldata[ktime_0rpm])))
                print('[calibrate_rawdata] channel %s has %s non0rpm samples'
                      % (nchan, len(self.caldata[ktime_non0rpm])))
            except KeyError:
                # This channel was always at 0rpm or always non0rpm
                pass
        # # debug
        # self.caldata = self.rawdata
        # print('[calibrate_rawdata] self.caldata.keys() %s'
        #       % self.caldata.keys())
        return self.caldata

    @staticmethod
    def apply_linreg(rpm):
        # ArsParser.strobelight_calib
        # Correction on arduSensor rpm to match StrobeLight rpm
        mx_slope = 1.101509798964998
        mx_intercept = -139.08974487011255
        rpm = mx_intercept + mx_slope * rpm
        return rpm

    def calculate_windata(self, window):
        self.windata = {}
        # wintime = np.arange(window, self.nsamples + 1)
        for nchan in range(0, self.nchannels):
            [ktime, krpm, kcur] = ArsParser.data_keys(nchan, '')
            arr = self.caldata[ktime]
            self.windata[ktime] = arr[window-1:]
            arr = self.caldata[krpm]
            self.windata[krpm] = ArsParser.moving_average(arr, window)
            arr = self.caldata[kcur]
            self.windata[kcur] = ArsParser.moving_average(arr, window)

            [ktime_0rpm, krpm_0rpm, kcur_0rpm] = \
                ArsParser.data_keys(nchan, '0rpm')
            try:
                arr = self.caldata[ktime_0rpm]
                self.windata[ktime_0rpm] = arr[window-1:]
                arr = self.caldata[krpm_0rpm]
                self.windata[krpm_0rpm] = ArsParser.moving_average(arr, window)
                arr = self.caldata[kcur_0rpm]
                self.windata[kcur_0rpm] = ArsParser.moving_average(arr, window)
            except KeyError:
                # This channel was always at 0rpm or always non0rpm
                pass

            [ktime_non0rpm, krpm_non0rpm, kcur_non0rpm] = \
                ArsParser.data_keys(nchan, 'non0rpm')
            try:
                arr = self.caldata[ktime_non0rpm]
                self.windata[ktime_non0rpm] = arr[window-1:]
                arr = self.caldata[krpm_non0rpm]
                self.windata[krpm_non0rpm] = ArsParser.moving_average(
                    arr, window)
                arr = self.caldata[kcur_non0rpm]
                self.windata[kcur_non0rpm] = ArsParser.moving_average(
                    arr, window)
            except KeyError:
                # This channel was always at 0rpm or always non0rpm
                pass

            # if nchan == 0:
            #     for key, value in self.caldata.items():
            #         print('[calculate_windata] len(self.caldata[%s]) %s'
            #               % (key, len(value)))
            #     for key, value in self.windata.items():
            #         print('[calculate_windata] len(self.windata[%s]) %s'
            #               % (key, len(value)))
        return self.windata

    @staticmethod
    def data_keys(nchan, kfilter):
        if kfilter == 'non0rpm':
            ktime = 'time%s_non0rpm' % nchan
            krpm = 'rpm%s_non0rpm' % nchan
            kcur = 'cur%s_non0rpm' % nchan
            return [ktime, krpm, kcur]
        elif kfilter == '0rpm':
            ktime = 'time%s_0rpm' % nchan
            krpm = 'rpm%s_0rpm' % nchan
            kcur = 'cur%s_0rpm' % nchan
            return [ktime, krpm, kcur]
        else:
            ktime = 'time%s' % nchan
            krpm = 'rpm%s' % nchan
            kcur = 'cur%s' % nchan
            return [ktime, krpm, kcur]

    @staticmethod
    def moving_average(x, window):
        movavg = np.convolve(x, np.ones(window), 'valid') / window
        # print('[moving_average] len(movavg) %s' % len(movavg))
        return movavg

    def plot_motors(self, pltdata):
        closefig = True
        for mpair in self.motor_pairs:
            for motor in mpair:
                nchan = self.motor_to_channel(motor)
                [ktime, krpm, kcur] = ArsParser.data_keys(nchan, '')
                time = pltdata[ktime]
                rpm = pltdata[krpm]
                cur = pltdata[kcur]

                [fig, ax_arr] = FigureTools.create_fig_axes(1, 1)
                _ = fig

                x_arr = [time, time]
                y_arr = [rpm, cur]
                xlabel_arr = ['Time s']
                ylabel_arr = ['Speed RPM', 'Current A']
                PlotTools.ax1_x2_y2_twinx(
                    ax_arr, x_arr, xlabel_arr, y_arr, ylabel_arr)

                firstname = \
                    self.arsfile_basename + '_' + self.plot_motors.__name__
                lastname = '_m%s' % motor
                filename = 'plots/' + firstname + lastname
                FigureTools.savefig(filename, closefig)

    def motor_to_channel(self, motor):
        return self.channel_arr[self.motor_arr.index(motor)]

    def channel_to_motor(self, nchan):
        return self.motor_arr[self.channel_arr.index(nchan)]

    def plot_arms(self, pltdata):
        closefig = True
        for mpair in self.motor_pairs:
            motor1 = mpair[0]
            motor2 = mpair[1]
            chan1 = self.motor_to_channel(motor1)
            chan2 = self.motor_to_channel(motor2)
            arg = '[plot_arms] chan1 ' + str(chan1) + ', motor1 ' + str(motor1)
            print(arg)
            arg = '[plot_arms] chan2 ' + str(chan2) + ', motor2 ' + str(motor2)
            print(arg)

            [ktime, krpm, kcur] = ArsParser.data_keys(chan1, '')
            time1 = pltdata[ktime]
            rpm1 = pltdata[krpm]
            cur1 = pltdata[kcur]

            [ktime, krpm, kcur] = ArsParser.data_keys(chan2, '')
            time2 = pltdata[ktime]
            rpm2 = pltdata[krpm]
            cur2 = pltdata[kcur]

            # Plot RPM
            [fig, ax_arr] = FigureTools.create_fig_axes(1, 1)
            _ = fig

            x_arr = [time1, time2]
            y_arr = [rpm1, rpm2]
            xlabel_arr = ['Time s']
            ylabel_arr = ['m%s RPM' % str(motor1), 'm%s RPM' % str(motor2)]
            PlotTools.ax1_x2_y2_twinx(
                ax_arr, x_arr, xlabel_arr, y_arr, ylabel_arr)

            firstname = self.arsfile_basename + '_' + self.plot_arms.__name__
            lastname = '_m%s_m%s' % (motor1, motor2)
            filename = 'plots/' + firstname + lastname + '_rpm'
            FigureTools.savefig(filename, closefig)

            # Plot current
            [fig, ax_arr] = FigureTools.create_fig_axes(1, 1)
            _ = fig

            x_arr = [time1, time2]
            y_arr = [cur1, cur2]
            xlabel_arr = ['Time s']
            ylabel_arr = ['m%s A' % str(motor1), 'm%s A' % str(motor2)]
            PlotTools.ax1_x2_y2_twinx(
                ax_arr, x_arr, xlabel_arr, y_arr, ylabel_arr)

            firstname = self.arsfile_basename + '_' + self.plot_arms.__name__
            lastname = '_m%s_m%s' % (motor1, motor2)
            filename = 'plots/' + firstname + lastname + '_cur'
            FigureTools.savefig(filename, closefig)

            # plt.show()

    def ulgfile_data(self):
        [csvname, x, status, controls, output, pwm_limited] = \
            UlgParser.get_toopazo_ctrlalloc_0(self.ulgfile, self.tmpdir)

        # [c0, c1, c2, c3] = controls
        # [o0, o1, o2, o3, o4, o5, o6, o7] = output
        # [p0, p1, p2, p3, p4, p5, p6, p7] = pwm_limited

        maxnum_nan = 250

        indx_nan = np.argwhere(np.isnan(status))
        num_nan = len(indx_nan)
        if num_nan <= maxnum_nan:
            status[indx_nan] = status[indx_nan-1]   # Assign previous value
        else:
            print('[ulgfile_data] Too many NaN in status[%s]' % indx_nan)
            print('[ulgfile_data] num_nan %s' % num_nan)

        for i in range(0, len(controls)):
            ctrli = controls[i]
            indx_nan = np.argwhere(np.isnan(ctrli))
            num_nan = len(indx_nan)
            if num_nan <= maxnum_nan:
                ctrli[indx_nan] = ctrli[indx_nan-1]   # Assign previous value
            else:
                print('[ulgfile_data] Too many NaN in controls[%s]' % i)
                print('[ulgfile_data] num_nan %s' % num_nan)

        for i in range(0, len(output)):
            outi = output[i]
            indx_nan = np.argwhere(np.isnan(outi))
            num_nan = len(indx_nan)
            if num_nan <= maxnum_nan:
                outi[indx_nan] = outi[indx_nan-1]   # Assign previous value
            else:
                print('[ulgfile_data] Too many NaN in output[%s]' % i)
                print('[ulgfile_data] num_nan %s' % num_nan)

        for i in range(0, len(pwm_limited)):
            pwmi = pwm_limited[i]
            indx_nan = np.argwhere(np.isnan(pwmi))
            num_nan = len(indx_nan)
            if num_nan <= maxnum_nan:
                pwmi[indx_nan] = pwmi[indx_nan-1]   # Assign previous value
            else:
                print('[ulgfile_data] Too many NaN in pwm_limited[%s]' % i)
                print('[ulgfile_data] num_nan %s' % num_nan)

        return [csvname, x, status, controls, output, pwm_limited]

    def calculate_syndata(self, pltdata, arsoffset):
        self.syndata = {}
        for mpair in self.motor_pairs:
            motor1 = mpair[0]
            motor2 = mpair[1]
            chan1 = self.motor_to_channel(motor1)
            chan2 = self.motor_to_channel(motor2)

            [ktime, krpm, kcur] = ArsParser.data_keys(chan1, '')
            time1 = pltdata[ktime]
            rpm1 = pltdata[krpm]
            cur1 = pltdata[kcur]

            [ktime, krpm, kcur] = ArsParser.data_keys(chan2, '')
            time2 = pltdata[ktime]
            rpm2 = pltdata[krpm]
            cur2 = pltdata[kcur]

            [csvname, x, status, controls, output, pwm_limited] = \
                self.ulgfile_data()
            _ = [csvname, controls]

            # Tolerance in sampling time error, measured in seconds
            # maximum unsigned deviation
            # t_dt_maxusgndev = 0.01
            # mean signed deviation
            t_dt_meansgndev = 10**-5
            tolkey = 't_dt_meansgndev'
            tolval = t_dt_meansgndev

            verbose = self.verbose
            if verbose:
                print('[calculate_syndata] Resample rpm1:')
            [rt1_arr, rx1_arr] = TimeseriesTools.resample(
                time1, rpm1, x, tolkey, tolval, verbose)
            _ = rt1_arr
            rpm1 = rx1_arr

            if verbose:
                print('[calculate_syndata] Resample cur1:')
            [rt1_arr, rx1_arr] = TimeseriesTools.resample(
                time1, cur1, x, tolkey, tolval, verbose)
            _ = rt1_arr
            cur1 = rx1_arr

            if verbose:
                print('[calculate_syndata] Resample rpm2:')
            [rt1_arr, rx1_arr] = TimeseriesTools.resample(
                time2, rpm2, x, tolkey, tolval, verbose)
            _ = rt1_arr
            rpm2 = rx1_arr

            if verbose:
                print('[calculate_syndata] Resample cur2:')
            [rt1_arr, rx1_arr] = TimeseriesTools.resample(
                time2, cur2, x, tolkey, tolval, verbose)
            _ = rt1_arr
            cur2 = rx1_arr

            outa = output[motor1 - 1]
            outb = output[motor2 - 1]

            pwma = pwm_limited[motor1 - 1]
            pwmb = pwm_limited[motor2 - 1]

            # Find optimum delay
            ioffset0 = arsoffset - 500
            ioffset1 = arsoffset + 500
            print('[calculate_syndata] Running ArsParser.cross_correlation ..')
            print('[calculate_syndata] arsoffset %s' % arsoffset)
            print('[calculate_syndata] ioffset0 %s, ioffset1 %s' %
                  (ioffset0, ioffset1))
            xcorr_dict = ArsParser.cross_correlation(
                pwma, rpm1, arsoffset-500, ioffset1)
            print('[calculate_syndata] xcorr_dict[ioffset0] %s'
                  % xcorr_dict['ioffset0'])

            # Synchronize ars and ulg files
            tx_nsamples = len(x)
            sync_offset = xcorr_dict['ioffset0']
            rpma = rpm1[sync_offset:(sync_offset+tx_nsamples)]
            rpmb = rpm2[sync_offset:(sync_offset+tx_nsamples)]
            cura = cur1[sync_offset:(sync_offset+tx_nsamples)]
            curb = cur2[sync_offset:(sync_offset+tx_nsamples)]

            # Ad-hoc current calibration
            cura = cura - cura[0]
            curb = curb - curb[0]

            # Ad-hoc output calibration
            outa = (outa + 1) / 2
            outb = (outb + 1) / 2

            # Ad-hoc status calibration
            status = (status - 1) * 0.9

            y_arr = [status, outa, pwma, rpma, cura, outb, pwmb, rpmb, curb]
            x_arr = [x]

            key = 'm%s_m%s' % (motor1, motor2)
            self.syndata[key] = {'x_arr': x_arr, 'y_arr': y_arr}

    def write_syndata_timebars(self, test_data, testkey):
        fpath = self.plotdir + '/' + testkey + '.pkl'
        syndata_timebars_arr = []
        for key, value in self.syndata.items():
            # y_arr = [status, outa, pwma, rpma, cura, outb, pwmb, rpmb, curb]
            # x_arr = [x]
            y_arr = value['y_arr']
            x_arr = value['x_arr']

            detected = False
            arsfile = test_data['arsfile']
            ulgfile = test_data['ulgfile']
            if self.arsfile == arsfile and self.ulgfile == ulgfile:
                detected = True
            if not detected:
                print('[write_syndata_timebars] File not detected')
                return
            try:
                iter(test_data['timebars'])
            except TypeError:
                print('[write_syndata_timebars] timebars is not iterable')
                return

            # Analyze timebars
            timebars = test_data['timebars']
            cnt = 1
            for tpair in timebars:
                i0 = tpair[0]
                i1 = tpair[1]

                # y_arr = \
                #     [status, outa, pwma, rpma, cura, outb, pwmb, rpmb, curb]
                # x_arr = [x]
                [status, outa, pwma, rpma, cura, outb, pwmb, rpmb, curb] = y_arr

                verbose = False
                status_d = TimeseriesTools.common_statistics(
                    status[i0:i1], verbose)

                outa_d = TimeseriesTools.common_statistics(outa[i0:i1], verbose)
                pwma_d = TimeseriesTools.common_statistics(pwma[i0:i1], verbose)
                rpma_d = TimeseriesTools.common_statistics(rpma[i0:i1], verbose)
                cura_d = TimeseriesTools.common_statistics(cura[i0:i1], verbose)

                outb_d = TimeseriesTools.common_statistics(outb[i0:i1], verbose)
                pwmb_d = TimeseriesTools.common_statistics(pwmb[i0:i1], verbose)
                rpmb_d = TimeseriesTools.common_statistics(rpmb[i0:i1], verbose)
                curb_d = TimeseriesTools.common_statistics(curb[i0:i1], verbose)

                # Use only mean and std
                status_mean = status_d['x_mean']
                status_std = status_d['x_std']

                outa_mean = outa_d['x_mean']
                outa_std = outa_d['x_std']
                pwma_mean = pwma_d['x_mean']
                pwma_std = pwma_d['x_std']
                rpma_mean = rpma_d['x_mean']
                rpma_std = rpma_d['x_std']
                cura_mean = cura_d['x_mean']
                cura_std = cura_d['x_std']

                # Use only mean and std
                outb_mean = outb_d['x_mean']
                outb_std = outb_d['x_std']
                pwmb_mean = pwmb_d['x_mean']
                pwmb_std = pwmb_d['x_std']
                rpmb_mean = rpmb_d['x_mean']
                rpmb_std = rpmb_d['x_std']
                curb_mean = curb_d['x_mean']
                curb_std = curb_d['x_std']

                [twin, dout_avg, dpwm_avg, drpm_avg, dcur_avg, tcur_avg] = \
                    ArsParser.calculate_deltas(x_arr, y_arr, i0, i1)

                syndata_timebars = [
                    key, cnt,
                    status_mean, status_std,
                    outa_mean, outa_std,
                    pwma_mean, pwma_std,
                    rpma_mean, rpma_std,
                    cura_mean, cura_std,
                    outb_mean, outb_std,
                    pwmb_mean, pwmb_std,
                    rpmb_mean, rpmb_std,
                    curb_mean, curb_std,
                    twin, dout_avg, dpwm_avg, drpm_avg, dcur_avg, tcur_avg
                ]
                syndata_timebars_arr.append(syndata_timebars)

                cnt = cnt + 1

                # fd.write(line)
        with open(fpath, 'wb') as fd:
            pickle.dump(syndata_timebars_arr, fd)
        # fd.close()

    def plot_syndata(self, test_data):
        closefig = True
        fnctname = self.plot_syndata.__name__
        for key, value in self.syndata.items():
            # print('[plot_syndata] Processing syndata[%s] = %s' % (key, value))

            m1_m2 = key.replace('m', '')
            m1_m2 = m1_m2.split('_')
            motor1 = int(m1_m2[0])
            motor2 = int(m1_m2[1])

            # y_arr = [status, outa, pwma, rpma, cura, outb, pwmb, rpmb, curb]
            # x_arr = [x]
            # [fig, ax_arr] = FigureTools.create_fig_axes(4, 1)
            # xlabel_arr = ['Time s']
            # status = value['y_arr'][0] - 1.6
            # y_arr = value['y_arr'][1:]
            # x_arr = value['x_arr']
            # ylabel_arr = ['Output', 'Throttle $\mu$s', 'RPM', 'Current, A']
            # PlotTools.ax4_x1_y8(ax_arr, x_arr, xlabel_arr, y_arr, ylabel_arr)

            # y_arr = [status, outa, pwma, rpma, cura, outb, pwmb, rpmb, curb]
            # x_arr = [x]
            # [fig, ax_arr] = FigureTools.create_fig_axes(3, 1)
            fig, ax_arr = plt.subplots(3, 1, figsize=[8, 6])
            xlabel_arr = ['']   # ['Time s']
            vy_arr = value['y_arr']
            status = vy_arr[0]
            y_arr = [vy_arr[1], vy_arr[3], vy_arr[4],
                     vy_arr[5], vy_arr[7], vy_arr[8]]
            x_arr = value['x_arr']
            ylabel_arr = ['Throttle', 'RPM', 'Current, A']
            PlotTools.ax3_x1_y6(ax_arr, x_arr, xlabel_arr, y_arr, ylabel_arr)
            nax = len(ax_arr)
            ax_arr[nax - 1].set(xlabel='Time s')

            arsfile = test_data['arsfile']
            if ('test11' in arsfile) or ('test12' in arsfile):
                # fig.suptitle('Timeseries for motors:\n'
                #              ' %s (red, upper) %s (green, lower)'
                #              % (motor1, motor2))
                pass
            else:
                # fig.suptitle('Timeseries: ulg and ars files from m%s and m%s'
                #              % (motor1, motor2))
                # fig.suptitle('Timeseries for motors:\n'
                #              ' %s (red, upper) %s (green, lower)'
                #              % (motor1, motor2))
                ax_arr[0].plot(
                    x_arr[0], status, color='black', linestyle='dashed')

            y_arr = value['y_arr']
            x_arr = value['x_arr']
            self.plot_syndata_add_info(ax_arr, x_arr, y_arr, test_data)

            firstname = self.arsfile_basename + '_' + fnctname
            lastname = '_m%s_m%s' % (motor1, motor2)
            filename = 'plots/' + firstname + lastname
            FigureTools.savefig(filename, closefig)

    def plot_syndata_add_info(self, ax_arr, x_arr, y_arr, test_data):
        detected = False
        arsfile = test_data['arsfile']
        ulgfile = test_data['ulgfile']
        if self.arsfile == arsfile and self.ulgfile == ulgfile:
            detected = True
        if not detected:
            print('[plot_syndata_timebars] File not detected')
            return
        try:
            iter(test_data['timebars'])
        except TypeError:
            print('[plot_syndata_timebars] timebars is not iterable')
            return

        # Set ylim
        ylim_arr = test_data['ylim_arr']
        nax = len(ax_arr)
        for indx in range(0, nax - 1):
            ax_arr[indx].set_ylim(ylim_arr[indx])
            ax_arr[indx].axes.xaxis.set_ticklabels([])
        ax_arr[nax - 1].set_ylim(ylim_arr[nax - 1])
        # ax_arr[nax-1].axes.xaxis.set_ticklabels([])

        # Add vlines
        timebars = test_data['timebars']
        for tpair in timebars:
            i0 = tpair[0]
            i1 = tpair[1]
            ArsParser.add_timebars(ax_arr, x_arr, y_arr, i0, i1, test_data)
            ArsParser.add_deltas(ax_arr, x_arr, y_arr, i0, i1, test_data)

        # Ad-hoc xlim
        arsfile = test_data['arsfile']
        if ('test11' in arsfile) or ('test12' in arsfile):
            xlim_arr = test_data['xlim_arr']
            nax = len(ax_arr)
            for indx in range(0, nax):
                ax_arr[indx].set_xlim(xlim_arr)
                # pass

    @staticmethod
    def calculate_deltas(x_arr, y_arr, i0, i1):
        # y_arr = [status, outa, pwma, rpma, cura, outb, pwmb, rpmb, curb]
        # x_arr = [x]
        [status, outa, pwma, rpma, cura, outb, pwmb, rpmb, curb] = y_arr
        _ = status
        time_arr = x_arr[0]

        # Mean dout per second
        dout_avg = np.mean(outa[i0:i1] - outb[i0:i1])  # / twin
        dpwm_avg = np.mean(pwma[i0:i1] - pwmb[i0:i1])  # / twin
        drpm_avg = np.mean(rpma[i0:i1] - rpmb[i0:i1])  # / twin
        dcur_avg = np.mean(cura[i0:i1] - curb[i0:i1])  # / twin
        tcur_avg = np.mean(cura[i0:i1] + curb[i0:i1])
        twin = time_arr[i1] - time_arr[i0]

        return [twin, dout_avg, dpwm_avg, drpm_avg, dcur_avg, tcur_avg]

    @staticmethod
    def add_deltas(ax_arr, x_arr, y_arr, i0, i1, test_data, **kwargs):
        [twin, dout_avg, dpwm_avg, drpm_avg, dcur_avg, tcur_avg] = \
            ArsParser.calculate_deltas(x_arr, y_arr, i0, i1)
        _ = twin

        # time_arr = x_arr[0]
        x_arr = x_arr[0]
        arsfile = test_data['arsfile']
        ylim_arr = test_data['ylim_arr']
        # units_arr = test_data['units_arr']
        bbox_dict = dict(facecolor='white', edgecolor='none', alpha=0.8)

        text_arr = []
        if len(ax_arr) == 3:
            text_arr = [
                '$\Delta$ %s' % round(float(dout_avg), 2),
                '$\Delta$ %s rpm' % int(round(float(drpm_avg))),
                '$\Delta$ %s A' % round(float(dcur_avg), 2)
            ]
        if len(ax_arr) == 4:
            text_arr = [
                '$\Delta$ %s' % round(float(dout_avg), 2),
                '$\Delta$ %s pwm' % int(round(float(dpwm_avg))),
                '$\Delta$ %s rpm' % int(round(float(drpm_avg))),
                '$\Delta$ %s A' % round(float(dcur_avg), 2)
            ]

        if ('test11' in arsfile) or ('test12' in arsfile):
            text_xy0 = test_data['text_xy0']
            for indx in range(0, len(ax_arr)):
                ax = ax_arr[indx]
                arg = text_arr[indx]
                xy0 = text_xy0[indx]
                x0 = x_arr[i0] + xy0[0]
                y0 = 0 + xy0[1]
                ax.text(x0, y0, arg, fontsize=14, color='black', bbox=bbox_dict)

            # Ad-hoc
            indx = len(ax_arr) - 1
            ax = ax_arr[indx]
            arg = 'tot %s A' % round(float(tcur_avg), 2)
            xy0 = text_xy0[indx]
            ylim = ylim_arr[indx]
            x0 = x_arr[i0] + xy0[0]
            y0 = ylim[1] * 0.75
            ax.text(x0, y0, arg, fontsize=14, color='black', bbox=bbox_dict)

            # Ad-hoc
            ax = ax_arr[0]
            arg = 'custom to default \n transition'
            transition = test_data['transition']
            x0 = transition['x0']
            y0 = transition['y0']
            x1 = transition['x1']
            y1 = transition['y1']
            ax.annotate(
                arg, xy=(x0, y0), xycoords='data', xytext=(x1, y1),
                fontsize=14, textcoords='data', arrowprops=dict(
                    arrowstyle="fancy", color="grey", patchB=None,
                    shrinkB=5, connectionstyle="arc3,rad=0.3", )
            )
            # bbox=bbox_dict

        # test1 to test10
        else:
            for indx in range(0, len(ax_arr)):
                ax = ax_arr[indx]
                ylim = ylim_arr[indx]
                arg = text_arr[indx]
                plt.sca(ax)
                x0 = x_arr[i0]  # x_arr[int(i0 * 0.5 + i1 * 0.5)]
                y0 = ylim[0] * 0.95 + ylim[1] * (1 - 0.95)
                ax.text(x0, y0, arg, fontsize=14, color='black', bbox=bbox_dict)

            # Ad-hoc
            indx = len(ax_arr) - 1
            ax = ax_arr[indx]
            ylim = ylim_arr[indx]
            arg = 'tot %s A' % round(float(tcur_avg), 2)
            plt.sca(ax)
            x0 = x_arr[i0]
            y0 = ylim[1] * 0.75
            ax.text(x0, y0, arg, fontsize=14, color='black', **kwargs)

    @staticmethod
    def add_timebars(ax_arr, x_arr, y_arr, i0, i1, test_data, **kwargs):
        ylim_arr = test_data['ylim_arr']

        # time_arr = x_arr[0]
        x_arr = x_arr[0]

        arsfile = test_data['arsfile']
        if ('test11' in arsfile) or ('test12' in arsfile):
            for indx in range(0, len(ax_arr)):
                ax = ax_arr[indx]
                ylim = ylim_arr[indx] * 0.9
                ymin = ylim[0]
                ymax = ylim[1]
                _ = y_arr

                x0 = x_arr[i0]
                ax.vlines(x=x0, ymin=ymin, ymax=ymax, colors='k',
                          linestyles='dashed', label='', **kwargs)
                x0 = x_arr[i1]
                ax.vlines(x=x0, ymin=ymin, ymax=ymax, colors='k',
                          linestyles='dashed', label='', **kwargs)
        else:
            indx = len(ax_arr) - 2
            ax = ax_arr[indx]
            ylim = ylim_arr[indx] * 0.9
            ymin = ylim[0]
            ymax = ylim[1]
            _ = y_arr

            x0 = x_arr[i0]
            ax.vlines(x=x0, ymin=ymin, ymax=ymax, colors='k',
                      linestyles='dashed', label='', **kwargs)
            x0 = x_arr[i1]
            ax.vlines(x=x0, ymin=ymin, ymax=ymax, colors='k',
                      linestyles='dashed', label='', **kwargs)

    @staticmethod
    def cross_correlation(xarr, yarr, ioffset0, ioffset1):
        xarr_nsamples = len(xarr)
        yarr_nsamples = len(yarr)

        if xarr_nsamples > yarr_nsamples:
            return None

        if ioffset0 < 0:
            ioffset0 = 0
            print('[cross_correlation] Warning ioffset0 < 0')
            print('[cross_correlation] xarr_nsamples %s' % xarr_nsamples)
            print('[cross_correlation] yarr_nsamples %s' % yarr_nsamples)

        if ioffset1 > yarr_nsamples:
            ioffset1 = yarr_nsamples
            print('[cross_correlation] Warning ioffset1 > yarr_nsamples')
            print('[cross_correlation] xarr_nsamples %s' % xarr_nsamples)
            print('[cross_correlation] yarr_nsamples %s' % yarr_nsamples)

        accum_arr = []
        for ioffset in range(ioffset0, ioffset1):
            accum = 0
            for i in range(0, xarr_nsamples):
                x1_y1 = xarr[i] * yarr[ioffset + i]
                accum = accum + x1_y1
            accum_arr.append(accum)
        i0 = np.argmax(np.array(accum_arr))
        ioffset0 = ioffset0 + i0

        rdict = {'accum_arr': accum_arr,
                 'ioffset0': ioffset0}

        return rdict


class StrobeLightCalib(ArsParser):
    def __init__(self, motor):
        self.motor = motor

        bdir = '/home/tzo4/Dropbox/tomas/pennState/avia/firefly_logBook/' \
               '2020-12-21_ars_calibration'
        if motor == 3:
            # Firefly motors 3 statically tested in mocap studio (no blade)
            arsfile = bdir + '/logs/' + 'log_dec21_test1.ars'
            # calib_throttle = [1200, 1300, 1160, 1170, 1150, 1140, 1130, 1126,
            #                   1220, 1190, 1170, 1180, 1210, 1230, 1240]
            calib_rpm = [2628, 3942, 1907, 2124, 1757, 1517, 1248, 1155,
                         2959, 2480, 2123, 2289, 2780, 3082, 3238]
            ulgfile = str(None)
        elif motor == 8:
            # Firefly motors 8 statically tested in mocap studio (no blade)
            arsfile = bdir + '/logs/' + 'log_dec21_test2.ars'
            # calib_throttle = [1200, 1300, 1160, 1170, 1150, 1140, 1130, 1126,
            #                   1220, 1190, 1170, 1180, 1210, 1230, 1240]
            calib_rpm = [2598, 3891, 1927, 2136, 1743, 1421, 1204, 1086, 2969,
                         2480, 2139, 2324, 2797, 3086, 3221]
            ulgfile = str(None)
        else:
            raise RuntimeError

        super().__init__(bdir, arsfile, ulgfile, False)
        # ArsParser.__init__(self, bdir, arsfile, ulgfile)

        self.nchan = self.motor_to_channel(self.motor)
        self.calib_rpm = calib_rpm

        [ktime, krpm, kcur] = ArsParser.data_keys(self.nchan, '')
        _ = kcur
        self.orig_time = self.caldata[ktime]    # windata[ktime]
        self.orig_rpm = self.caldata[krpm]      # windata[krpm]

        [ktime, krpm, kcur] = ArsParser.data_keys(self.nchan, 'non0rpm')
        _ = kcur
        self.non0rpm_time = self.caldata[ktime]
        self.non0rpm_rpm = self.caldata[krpm]

        self.avgtwin_rpm = None

    def strobelight_calib(self):
        motor = self.motor
        calib_rpm = self.calib_rpm

        print('\n\nRunning strobelight calibration with motor %s' % motor)

        self.strobelight_calib_plot_orig()

        avgtwin_rpm = self.strobelight_calib_avgtwin_rpm()

        # Ad-hoc edition to calib_rpm and avgtwin_rpm
        if motor == 3:
            avgtwin_rpm.pop(0)
            calib_rpm.sort()
            avgtwin_rpm.sort()
            calib_rpm = np.array(calib_rpm)
            avgtwin_rpm = np.array(avgtwin_rpm)
        elif motor == 8:
            # avgtwin_rpm.pop(0)
            calib_rpm.sort()
            avgtwin_rpm.sort()
            calib_rpm = np.array(calib_rpm)
            avgtwin_rpm = np.array(avgtwin_rpm)
            # pass

        # Update calib_rpm and avgtwin
        self.calib_rpm = calib_rpm
        self.avgtwin_rpm = avgtwin_rpm

        # Linear regression
        x = avgtwin_rpm
        y = calib_rpm
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        print('slope %s, intercept %s, r_value %s, p_value %s, std_err %s'
              % (slope, intercept, r_value, p_value, std_err))
        linreg_rpm = intercept + slope * np.array(avgtwin_rpm)

        self.strobelight_calib_plot_calib(
            avgtwin_rpm, linreg_rpm, slope, intercept)

        self.strobelight_calib_plot_linearity(avgtwin_rpm, linreg_rpm)

        return [slope, intercept]

    def strobelight_calib_plot_savefig(self, fnctname):
        basename = self.arsfile_basename
        firstname = basename + '_' + fnctname
        lastname = 'm%s' % self.motor
        filename = self.plotdir + '/' + firstname + '_' + lastname
        FigureTools.savefig(filename, closefig=False)

    def strobelight_calib_plot_linearity(self, avgtwin_rpm, linreg_rpm):
        calib_rpm = self.calib_rpm

        # Plot linearity
        [fig, ax_arr] = FigureTools.create_fig_axes(1, 1)
        _ = fig

        x_arr = [calib_rpm, calib_rpm]
        y_arr = [avgtwin_rpm, linreg_rpm]
        xlabel_arr = ['StrobeLight RPM']
        ylabel_arr = ['arduSensor RPM', 'LinReg RPM']
        PlotTools.ax1_x2_y2_twinx(
            ax_arr, x_arr, xlabel_arr, y_arr, ylabel_arr)

        plt.text(1100, 3500, 'arduSensor', fontsize=14, color='red')
        plt.text(1100, 3300, 'LinReg', fontsize=14, color='green')
        ax_arr[0].set_xlim([1000, 4000])
        ax_arr[0].set_ylim([1000, 4000])
        ax2 = plt.gca()
        ax2.set_ylim([1000, 4000])
        # ax_arr[0].set_xlim([0, t_arr[-1]+1])
        ax_arr[0].grid(True)

        # firstname = arsfile_basename + '_' + ArsParser.\
        #     strobelight_calib.__name__
        # lastname = '_m' + str(motor)
        # filename = 'plots/' + firstname + lastname + '_linearity'
        # FigureTools.savefig(filename, closefig=False)
        self.strobelight_calib_plot_savefig(
            self.strobelight_calib_plot_linearity.__name__)

    def strobelight_calib_plot_calib(
            self, avgtwin_rpm, linreg_rpm, slope, intercept):
        calib_rpm = self.calib_rpm

        # RMS error
        sqerr = (avgtwin_rpm - calib_rpm) * (avgtwin_rpm - calib_rpm)
        avgtwin_rms_error = np.sqrt(np.average(sqerr))
        print('RMS error (arduSensor) %s RPM' % avgtwin_rms_error)
        sqerr = (linreg_rpm - calib_rpm) * (linreg_rpm - calib_rpm)
        linreg_rms_error = np.sqrt(np.average(sqerr))
        print('RMS error (LinReg) %s RPM' % linreg_rms_error)

        # Plot test points
        [fig, ax_arr] = FigureTools.create_fig_axes(1, 1)
        _ = fig

        t_arr = list(range(1, len(calib_rpm)+1))
        x_arr = [t_arr, t_arr, t_arr]
        y_arr = [calib_rpm, avgtwin_rpm, linreg_rpm]
        xlabel_arr = ['Test points']
        ylabel_arr = ['Motor speed RPM']
        PlotTools.ax1_x3_y3(
            ax_arr, x_arr, xlabel_arr, y_arr, ylabel_arr)

        plt.text(1, 3500, 'StrobeLight', fontsize=14, color='red')
        plt.text(1, 3300, 'arduSensor', fontsize=14, color='green')
        arg = 'LinReg (slope %s, intercept %s)' \
              % (round(slope, 4), round(intercept, 4))
        plt.text(1, 3100, arg, fontsize=14, color='blue')
        arg = 'RMS error (arduSensor) %s RPM' % round(avgtwin_rms_error, 2)
        plt.text(1, 2900, arg, fontsize=14, color='black')
        arg = 'RMS error (LinReg) %s RPM' % round(linreg_rms_error, 2)
        plt.text(1, 2700, arg, fontsize=14, color='black')
        ax_arr[0].set_ylim([1000, 4000])
        ax_arr[0].set_xlim([0, t_arr[-1]+1])
        ax_arr[0].grid(True)

        # firstname = arsfile_basename + '_' + ArsParser.\
        #     strobelight_calib.__name__
        # lastname = '_m' + str(motor)
        # filename = 'plots/' + firstname + lastname + '_calib'
        # FigureTools.savefig(filename, closefig=False)
        self.strobelight_calib_plot_savefig(
            self.strobelight_calib_plot_calib.__name__)

    def strobelight_calib_plot_orig(self):
        orig_time = self.orig_time
        orig_rpm = self.orig_rpm
        calib_rpm = self.calib_rpm

        # print('arsparser_rpm %s' % arsparser_rpm)
        print('len(orig_rpm) %s' % len(orig_rpm))

        calib_time = np.linspace(
            orig_time[0], orig_time[-1], len(calib_rpm))

        # Plot RPM
        [fig, ax_arr] = FigureTools.create_fig_axes(1, 1)
        _ = fig

        x_arr = [orig_time, calib_time]
        y_arr = [orig_rpm, calib_rpm]
        xlabel_arr = ['Time s']
        ylabel_arr = ['arduSensor', 'StrobeLight']
        PlotTools.ax1_x2_y2_twinx(
            ax_arr, x_arr, xlabel_arr, y_arr, ylabel_arr)
        ax_arr[0].set_ylim([0, 4000])
        ax2 = plt.gca()
        ax2.set_ylim([0, 4000])

        # firstname = arsfile_basename + '_' + ArsParser.\
        #     strobelight_calib.__name__
        # lastname = '_m' + str(motor) + '_orig'
        # filename = 'plots/' + firstname + lastname
        # FigureTools.savefig(filename, closefig=False)
        self.strobelight_calib_plot_savefig(
            self.strobelight_calib_plot_orig.__name__)

    def strobelight_calib_avgtwin_rpm(self):
        non0rpm_time = self.non0rpm_time
        non0rpm_rpm = self.non0rpm_rpm

        # Find the index of non-consecutive non0rpm_time, this indicates
        # the change between pulses of non0rpm in the calibration file
        delta_index = np.where(np.diff(non0rpm_time) > 1)
        delta_index = list(delta_index[0])
        print('delta_index %s' % delta_index)

        avgtwin_rpm = []
        prev_ind = 0
        cnt = 1
        for ind in delta_index:
            ramp_effect = 4
            i0 = prev_ind + ramp_effect
            i1 = ind - ramp_effect
            twinlen = i1 - i0
            # twinlen = ind - ramp_effect - prev_ind - ramp_effect
            # twinlen = ind - prev_ind - 2*ramp_effect
            # if (ind - prev_ind) > (ramp_effect*2 + 1):
            if twinlen > 3:
                rpm_pulse = non0rpm_rpm[i0:i1]
                avgrpm = np.average(rpm_pulse)
                print('cnt %s, twin at index %s, average in rpm[%s, %s] is %s'
                      % (cnt, ind, i0, i1, avgrpm))
                avgtwin_rpm.append(avgrpm)
                cnt = cnt + 1
            else:
                # raise RuntimeError('(ind - prev_ind) > (ramp_effect*2 + 1)')
                print('transition at index %s, twinlen %s too short to be a '
                      'valid calibration point'
                      % (ind, twinlen))
            prev_ind = ind
        # print(non0rpm_time[0:10])
        # print(np.diff(non0rpm_time)[0:10])
        # print(delta_index)
        # print(avgtwin_rpm)

        print('len(calib_rpm) %s' % len(self.calib_rpm))
        print('calib_rpm %s' % self.calib_rpm)
        print('len(avgtwin_rpm) %s' % len(avgtwin_rpm))
        print('avgtwin_rpm %s' % avgtwin_rpm)

        return avgtwin_rpm


if __name__ == '__main__':
    # arg = '''
    # Before calibrating remember to comment line
    # rpm = ArsParser.apply_linreg(rpm)
    # in method ArsParser.calibrate_rawdata
    # '''
    # print(arg)
    #
    # m3_motor = 3
    # m3_calib = StrobeLightCalib(m3_motor)
    # [m3_slope, m3_intercept] = m3_calib.strobelight_calib()
    #
    # m8_motor = 8
    # m8_calib = StrobeLightCalib(m8_motor)
    # [m8_slope, m8_intercept] = m8_calib.strobelight_calib()
    #
    # m38_slope = np.average([m3_slope, m8_slope])
    # m38_intercept = np.average([m3_intercept, m8_intercept])
    # print('m38_slope %s' % m38_slope)
    # print('m38_intercept %s' % m38_intercept)
    # # m38_slope 1.101509798964998
    # # m38_intercept -139.08974487011255
    # exit(0)

    parser = argparse.ArgumentParser(
        description='Parse, process and plot .ulg files')
    parser.add_argument('--testnum', action='store', required=False,
                        help='Test number, as indicated in ars_dec22_data.py')
    parser.add_argument('--testall', action='store_true', required=False,
                        help='Test all cases indicated in ars_dec22_data.py')
    user_args = parser.parse_args()

    if user_args.testnum is not None:
        u_testkey = 'test%s' % int(user_args.testnum)
        u_test_data = ArsDec22Data.test_db[u_testkey]
        u_bdir = u_test_data['bdir']
        u_arsfile = u_test_data['arsfile']
        u_ulgfile = u_test_data['ulgfile']
        u_arsoffset = u_test_data['arsoffset']

        u_verbose = False
        uarsparser = ArsParser(u_bdir, u_arsfile, u_ulgfile, u_verbose)
        # uarsparser.plot()
        uarsparser.calculate_syndata(uarsparser.windata, u_arsoffset)
        uarsparser.plot_syndata(u_test_data)
        uarsparser.write_syndata_timebars(u_test_data, u_testkey)

    if user_args.testall:
        for testi in range(1, 11):
            u_testkey = 'test%s' % testi
            u_test_data = ArsDec22Data.test_db[u_testkey]
            u_bdir = u_test_data['bdir']
            u_arsfile = u_test_data['arsfile']
            u_ulgfile = u_test_data['ulgfile']
            u_arsoffset = u_test_data['arsoffset']

            u_verbose = False
            uarsparser = ArsParser(u_bdir, u_arsfile, u_ulgfile, u_verbose)
            # uarsparser.plot()
            uarsparser.calculate_syndata(uarsparser.windata, u_arsoffset)
            uarsparser.plot_syndata(u_test_data)
            uarsparser.write_syndata_timebars(u_test_data, u_testkey)

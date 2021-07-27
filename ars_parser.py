#!/usr/bin/env python

from toopazo_tools.matplotlib import FigureTools, PlotTools, plt
from toopazo_tools.file_folder import FileFolderTools
from toopazo_tools.time_series import TimeseriesTools as tstools
from toopazo_tools.data2d import Data2D
from toopazo_ulg.file_parser import UlgParser
from toopazo_ulg.plot_main import UlgMain


from ars_dec22_data import ArsDec22Data

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

    def plot_basic_ulgdata(self):
        ulgfile = self.ulgfile
        closefig = True
        self.ulgmain.ulg_plot_basics.actuator_controls_0_0(ulgfile, closefig)
        self.ulgmain.ulg_plot_basics.actuator_outputs_0(ulgfile, closefig)
        self.ulgmain.ulg_plot_basics.vehicle_local_position_0(ulgfile, closefig)
        self.ulgmain.ulg_plot_basics.manual_control_setpoint_0(ulgfile, closefig)
        self.ulgmain.ulg_plot_basics.vehicle_rates_setpoint_0(ulgfile, closefig)
        self.ulgmain.ulg_plot_basics.vehicle_attitude_0_deg(ulgfile, closefig)
        self.ulgmain.ulg_plot_basics.nwindow_hover_pos(ulgfile, closefig)
        self.ulgmain.ulg_plot_basics.nwindow_hover_vel(ulgfile, closefig)

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

    def plot_mixer_ulgdata(self):
        # pltdata = self.rawdata
        # pltdata = self.caldata
        pltdata = self.windata

        # self.plot_motors(pltdata)
        # self.plot_arms(pltdata)

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
        fnctname = self.plot_motors.__name__

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

                motor1 = motor
                motor2 = ''
                self.save_plt(fnctname, motor1, motor2)

    def motor_to_channel(self, motor):
        return self.channel_arr[self.motor_arr.index(motor)]

    def channel_to_motor(self, nchan):
        return self.motor_arr[self.channel_arr.index(nchan)]

    def plot_arms(self, pltdata):
        fnctname = self.plot_arms.__name__

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

            motor2 = "%s_%s" % (motor2, 'rpm')
            self.save_plt(fnctname, motor1, motor2)

            # Plot current
            [fig, ax_arr] = FigureTools.create_fig_axes(1, 1)
            _ = fig

            x_arr = [time1, time2]
            y_arr = [cur1, cur2]
            xlabel_arr = ['Time s']
            ylabel_arr = ['m%s A' % str(motor1), 'm%s A' % str(motor2)]
            PlotTools.ax1_x2_y2_twinx(
                ax_arr, x_arr, xlabel_arr, y_arr, ylabel_arr)

            motor2 = "%s_%s" % (motor2, 'cur')
            self.save_plt(fnctname, motor1, motor2)

            # plt.show()

    def ulgfile_vehicle_attitude_0_deg(self):
        [csvname, tva, roll, pitch, yaw] = \
            UlgParser.get_vehicle_attitude_0_deg(self.ulgfile, self.tmpdir)

        attitude = Data2D.to_np_array([roll, pitch, yaw])
        maxnum_nan = 250
        attitude = Data2D.search_and_replace_nan(attitude, maxnum_nan)

        return [csvname, tva, attitude]

    def ulgfile_vehicle_local_position_0(self):
        [csvname, tvlp, px, py, pz, vx, vy, vz, ax, ay, az] = \
            UlgParser.get_vehicle_local_position_0(self.ulgfile, self.tmpdir)

        locpva = Data2D.to_np_array([px, py, pz, vx, vy, vz, ax, ay, az])
        maxnum_nan = 250
        locpva = Data2D.search_and_replace_nan(locpva, maxnum_nan)

        return [csvname, tvlp, locpva]

    def ulgfile_manual_control_setpoint_0(self):
        [csvname, tmcs, y0, y1, y2, y3] = \
            UlgParser.get_manual_control_setpoint_0(self.ulgfile, self.tmpdir)

        manctrl = Data2D.to_np_array([y0, y1, y2, y3])
        maxnum_nan = 250
        manctrl = Data2D.search_and_replace_nan(manctrl, maxnum_nan)

        return [csvname, tmcs, manctrl]

    def ulgfile_actuator_controls_0_0(self):
        [csvname, tac, y0, y1, y2, y3] = \
            UlgParser.get_actuator_controls_0_0(self.ulgfile, self.tmpdir)

        actctrl = Data2D.to_np_array([y0, y1, y2, y3])
        maxnum_nan = 250
        actctrl = Data2D.search_and_replace_nan(actctrl, maxnum_nan)

        return [csvname, tac, actctrl]

    def ulgfile_actuator_outputs_0(self):
        [csvname, tao, y0, y1, y2, y3, y4, y5, y6, y7] = \
            UlgParser.get_actuator_outputs_0(self.ulgfile, self.tmpdir)

        actout = Data2D.to_np_array([y0, y1, y2, y3, y4, y5, y6, y7])
        maxnum_nan = 250
        actout = Data2D.search_and_replace_nan(actout, maxnum_nan)

        return [csvname, tao, actout]

    def ulgfile_toopazo_ctrlalloc_0(self):
        [csvname, ttc, status, controls, output, pwm_limited] = \
            UlgParser.get_toopazo_ctrlalloc_0(self.ulgfile, self.tmpdir)

        # s0 = status
        # [c0, c1, c2, c3] = controls
        # [o0, o1, o2, o3, o4, o5, o6, o7] = output
        # [p0, p1, p2, p3, p4, p5, p6, p7] = pwm_limited

        maxnum_nan = 250
        status = [status]
        status = Data2D.to_np_array(status)
        status = Data2D.search_and_replace_nan(status, maxnum_nan)
        status = status[0]

        controls = Data2D.to_np_array(controls)
        controls = Data2D.search_and_replace_nan(controls, maxnum_nan)

        output = Data2D.to_np_array(output)
        output = Data2D.search_and_replace_nan(output, maxnum_nan)

        pwm_limited = Data2D.to_np_array(pwm_limited)
        pwm_limited = Data2D.search_and_replace_nan(pwm_limited, maxnum_nan)

        return [csvname, ttc, status, controls, output, pwm_limited]

    def upsample_arsdata(self, arsdata, motor1, motor2, new_time):
        chan1 = self.motor_to_channel(motor1)
        chan2 = self.motor_to_channel(motor2)

        [ktime, krpm, kcur] = ArsParser.data_keys(chan1, '')
        # time1 = self.windata[ktime]
        # rpm1 = self.windata[krpm]
        # cur1 = self.windata[kcur]
        time1 = arsdata[ktime]
        rpm1 = arsdata[krpm]
        cur1 = arsdata[kcur]

        [ktime, krpm, kcur] = ArsParser.data_keys(chan2, '')
        # time2 = self.windata[ktime]
        # rpm2 = self.windata[krpm]
        # cur2 = self.windata[kcur]
        time2 = arsdata[ktime]
        rpm2 = arsdata[krpm]
        cur2 = arsdata[kcur]

        # Tolerance in sampling time error, measured in seconds
        # maximum unsigned deviation
        # t_dt_maxusgndev = 0.01
        # mean signed deviation
        t_dt_meansgndev = 10 ** -5
        tolkey = 't_dt_meansgndev'
        tolval = t_dt_meansgndev

        # Resample .ars data to match the SPS of .ulg data

        motor1_data2d = Data2D.to_np_array([rpm1, cur1])
        (motor1_time, motor1_data2d) = Data2D.upsample_data2d(
            data2d_time=time1, data2d=motor1_data2d, new_time=new_time,
            tolkey=tolkey, tolval=tolval)
        time1 = motor1_time
        rpm1 = motor1_data2d[0]
        cur1 = motor1_data2d[1]

        motor2_data2d = Data2D.to_np_array([rpm2, cur2])
        (motor2_time, motor2_data2d) = Data2D.upsample_data2d(
            data2d_time=time2, data2d=motor2_data2d, new_time=new_time,
            tolkey=tolkey, tolval=tolval)
        time2 = motor2_time
        rpm2 = motor2_data2d[0]
        cur2 = motor2_data2d[1]

        [ktime, krpm, kcur] = ArsParser.data_keys(chan1, '')
        # self.windata[ktime] = time1
        # self.windata[krpm] = rpm1
        # self.windata[kcur] = cur1
        arsdata[ktime] = time1
        arsdata[krpm] = rpm1
        arsdata[kcur] = cur1

        [ktime, krpm, kcur] = ArsParser.data_keys(chan2, '')
        # self.windata[ktime] = time2
        # self.windata[krpm] = rpm2
        # self.windata[kcur] = cur2
        arsdata[ktime] = time2
        arsdata[krpm] = rpm2
        arsdata[kcur] = cur2

        return arsdata

    def calculate_syndata(self, arsdata, arsoffset):
        self.syndata = {}
        for mpair in self.motor_pairs:
            motor1 = mpair[0]
            motor2 = mpair[1]
            chan1 = self.motor_to_channel(motor1)
            chan2 = self.motor_to_channel(motor2)

            [csvname, ttc, status, controls, output, pwm_limited] = \
                self.ulgfile_toopazo_ctrlalloc_0()
            _ = [csvname, controls]

            # Resample .ars data to match the SPS of .ulg data
            arsdata = self.upsample_arsdata(
                arsdata, motor1, motor2, new_time=ttc)

            [ktime, krpm, kcur] = ArsParser.data_keys(chan1, '')
            time1 = arsdata[ktime]
            rpm1 = arsdata[krpm]
            cur1 = arsdata[kcur]

            [ktime, krpm, kcur] = ArsParser.data_keys(chan2, '')
            time2 = arsdata[ktime]
            rpm2 = arsdata[krpm]
            cur2 = arsdata[kcur]

            # print('[calculate_syndata] time_statistics(time1, True)')
            # tstools.time_statistics(time1, True)
            # print('[calculate_syndata] time_statistics(time2, True)')
            # tstools.time_statistics(time2, True)
            # print('[calculate_syndata] time_statistics(ttc, True)')
            # tstools.time_statistics(ttc, True)

            # Select pairs from .ulg data

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
            tx_nsamples = len(ttc)
            sync_offset = xcorr_dict['ioffset0']
            timea = time1[sync_offset:(sync_offset + tx_nsamples)]
            timeb = time2[sync_offset:(sync_offset + tx_nsamples)]
            rpma = rpm1[sync_offset:(sync_offset + tx_nsamples)]
            rpmb = rpm2[sync_offset:(sync_offset + tx_nsamples)]
            cura = cur1[sync_offset:(sync_offset + tx_nsamples)]
            curb = cur2[sync_offset:(sync_offset + tx_nsamples)]

            # Ad-hoc current calibration
            cura = cura - cura[0]
            curb = curb - curb[0]

            # Ad-hoc output calibration
            outa = (outa + 1) / 2
            outb = (outb + 1) / 2

            # Ad-hoc status calibration
            status = (status - 1) * 0.9

            print('[calculate_syndata] timea[0] %s, timea[-1] %s'
                  % (timea[0], timea[-1]))
            print('[calculate_syndata] timeb[0] %s, timeb[-1] %s'
                  % (timeb[0], timeb[-1]))
            print('[calculate_syndata] ttc[0] %s, ttc[-1] %s'
                  % (ttc[0], ttc[-1]))

            # print('[calculate_syndata] np.array(timea - ttc).mean() %s'
            #       % str(np.array(timea - ttc).mean()))
            # print('[calculate_syndata] np.array(timeb - ttc).mean() %s'
            #       % str(np.array(timeb - ttc).mean()))

            y_arr = [status, outa, pwma, rpma, cura, outb, pwmb, rpmb, curb]
            x_arr = [ttc]

            y_arr = Data2D.to_np_array(y_arr)
            nan_indx = np.argwhere(np.isnan(y_arr))
            # print(nan_indx)
            print('[calculate_syndata] nan_indx.shape ', nan_indx.shape)
            y_arr_shape = y_arr.shape
            print('[calculate_syndata] np.array(y_arr).shape ', y_arr_shape)
            y_arr = np.nan_to_num(
                y_arr, copy=False, nan=0.0, posinf=None, neginf=None)
            nan_indx = np.argwhere(np.isnan(y_arr))
            print('[calculate_syndata] nan_indx.shape ', nan_indx.shape)

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
                # i0 = tpair[0]
                # i1 = tpair[1]
                t_arr = np.array(x_arr[0])
                i0, t0 = tstools.closest_element(tpair[0], t_arr)
                i1, t1 = tstools.closest_element(tpair[1], t_arr)

                # y_arr = \
                #     [status, outa, pwma, rpma, cura, outb, pwmb, rpmb, curb]
                # x_arr = [x]
                [status, outa, pwma, rpma, cura, outb, pwmb, rpmb, curb] = y_arr

                verbose = False
                status_d = tstools.common_statistics(
                    status[i0:i1], verbose)

                outa_d = tstools.common_statistics(outa[i0:i1], verbose)
                pwma_d = tstools.common_statistics(pwma[i0:i1], verbose)
                rpma_d = tstools.common_statistics(rpma[i0:i1], verbose)
                cura_d = tstools.common_statistics(cura[i0:i1], verbose)

                outb_d = tstools.common_statistics(outb[i0:i1], verbose)
                pwmb_d = tstools.common_statistics(pwmb[i0:i1], verbose)
                rpmb_d = tstools.common_statistics(rpmb[i0:i1], verbose)
                curb_d = tstools.common_statistics(curb[i0:i1], verbose)

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
        fnctname = self.plot_syndata.__name__

        for key, value in self.syndata.items():
            # print('[plot_syndata] Processing syndata[%s] = %s' % (key, value))

            # Unpack key
            m1_m2 = key.replace('m', '')
            m1_m2 = m1_m2.split('_')
            motor1 = int(m1_m2[0])
            motor2 = int(m1_m2[1])

            # Unpack value
            # y_arr = [status, outa, pwma, rpma, cura, outb, pwmb, rpmb, curb]
            # x_arr = [x]
            value_y_arr = value['y_arr']
            value_x_arr = value['x_arr']

            # Plot value_y_arr figure

            # y_arr = [status, outa, pwma, rpma, cura, outb, pwmb, rpmb, curb]
            # x_arr = [x]
            # [fig, ax_arr] = FigureTools.create_fig_axes(4, 1)
            # xlabel_arr = ['Time s']
            # status = value['y_arr'][0] - 1.6
            # y_arr = value['y_arr'][1:]
            # x_arr = value['x_arr']
            # ylabel_arr = ['Output', 'Throttle $\mu$s', 'RPM', 'Current, A']
            # PlotTools.ax4_x1_y8(ax_arr, x_arr, xlabel_arr, y_arr, ylabel_arr)

            # [fig, ax_arr] = FigureTools.create_fig_axes(3, 1)
            fig, ax_arr = plt.subplots(3, 1, figsize=[8, 6])
            xlabel_arr = ['']   # ['Time s']
            y_arr = [value_y_arr[1], value_y_arr[3], value_y_arr[4],
                     value_y_arr[5], value_y_arr[7], value_y_arr[8]]
            x_arr = value_x_arr
            ylabel_arr = ['Throttle', 'RPM', 'Current, A']
            PlotTools.ax3_x1_y6(ax_arr, x_arr, xlabel_arr, y_arr, ylabel_arr)
            nax = len(ax_arr)
            ax_arr[nax - 1].set(xlabel='Time s')

            # Add status to ax_arr[0]
            arsfile = test_data['arsfile']
            c1 = ('test11' in arsfile) or ('test12' in arsfile)
            if not c1:
                # Add status data
                status = value_y_arr[0]
                ax_arr[0].plot(
                    x_arr[0], status, color='black', linestyle='dashed')

            self.plot_syndata_add_info(ax_arr, x_arr, y_arr, test_data)

            self.save_plt(fnctname, motor1, motor2)

    def plot_syndata_add_info(self, ax_arr, x_arr, y_arr, test_data):
        # maxnum_nan = 100
        # y_arr = Data2D.search_and_replace_nan(y_arr, maxnum_nan)
        y_arr = np.nan_to_num(
            y_arr, copy=False, nan=0.0, posinf=None, neginf=None)

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

        c1 = (len(ax_arr) == 3) and (len(y_arr) == 6)
        c2 = (len(ax_arr) == 4) and (len(y_arr) == 8)
        if c1 or c2:
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
            # i0 = tpair[0]
            # i1 = tpair[1]
            t_arr = np.array(x_arr[0])
            i0, t0 = tstools.closest_element(tpair[0], t_arr)
            i1, t1 = tstools.closest_element(tpair[1], t_arr)
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

    def find_hover_timebars(self, test_data):
        fnctname = self.find_hover_timebars.__name__

        [csvname, tmcs, manctrl] = self.ulgfile_manual_control_setpoint_0()
        _ = [csvname]
        # https://github.com/PX4/PX4-Autopilot/blob/master/
        # msg/manual_control_setpoint.msg
        man_pitch = manctrl[0]
        man_roll = manctrl[1]
        man_throttle = manctrl[2]
        man_yaw = manctrl[3]
        man_attnorm_arr = Data2D.norm([man_pitch, man_roll], 0, None)
        _ = man_yaw

        [csvname, tac, actctrl] = self.ulgfile_actuator_controls_0_0()
        _ = [csvname]
        act_roll = actctrl[0]
        act_pitch = actctrl[1]
        act_yaw = actctrl[2]
        act_throttle = actctrl[3]
        act_attnorm_arr = Data2D.norm([act_pitch, act_roll], 0, None)
        _ = [tac, act_yaw, act_throttle, act_attnorm_arr]

        [csvname, tvlp, locpva] = self.ulgfile_vehicle_local_position_0()
        _ = [csvname]
        pos = locpva[0:3]
        vel = locpva[3:6]
        acc = locpva[6:9]
        pnorm_arr = Data2D.norm(pos, 0, None)
        vnorm_arr = Data2D.norm(vel, 0, None)
        anorm_arr = Data2D.norm(acc, 0, None)
        _ = [tvlp, pnorm_arr, vnorm_arr, anorm_arr]

        print('Estimate hover throttle')
        # hover_throttle = self.estimate_throttle(man_throttle)
        hover_throttle = np.percentile(np.unique(man_throttle), 50)
        print('  hover_throttle %s' % hover_throttle)

        # htperc = 0.98
        # threshold = np.percentile(man_throttle, 50)
        # threshold = np.percentile(np.unique(man_throttle), 80)
        threshold = 0.90 * hover_throttle
        # print(threshold)
        print('Time windows near hover')
        print('  threshold %s' % threshold)
        iwin1_arr, vwin1_arr = tstools.elements_satisfying_condition(
            man_throttle, operator.gt, threshold)
        twin1_arr = []
        for iwin1 in iwin1_arr:
            twin1 = tmcs[list(iwin1)]
            if twin1[-1] - twin1[0] >= 5.0:
                twin1_arr.append(twin1)
        twin1_arr = np.array(twin1_arr, dtype=object)
        for twin1 in twin1_arr:
            print('  twin1[0] %s, twin1[-1] %s' % (twin1[0], twin1[-1]))

        print('Time windows near zero cmd att')
        # threshold = np.percentile(np.unique(man_attnorm_arr), 70)
        man_min = np.min(man_attnorm_arr)
        man_max = np.max(man_attnorm_arr)
        alpha = 0.5
        threshold = man_min * (1 - alpha) + man_max * alpha
        print('  threshold %s' % threshold)
        iwin2_arr, vwin2_arr = tstools.elements_satisfying_condition(
            man_attnorm_arr, operator.le, threshold)
        twin2_arr = []
        for iwin2 in iwin2_arr:
            twin2 = tmcs[iwin2]
            twin2_arr.append(twin2)
        twin2_arr = np.array(twin2_arr, dtype=object)
        for twin2 in twin2_arr:
            print('  twin2[0] %s, twin2[-1] %s' % (twin2[0], twin2[-1]))

        print('Time windows satisfying both conditions')
        if (len(twin1_arr) != 2) or (len(twin2_arr) < 2):
            raise RuntimeError
        twin_data2d = []
        for twin1 in twin1_arr:
            twin3_arr = tstools.overlapping_time_windows(
                [twin1], twin2_arr, min_delta=1.0)
            twin_data2d.append(twin3_arr)
        twin_data2d = np.array(twin_data2d, dtype=object)
        for twin3_arr in twin_data2d:
            print('  twin3_arr %s' % twin3_arr)

        # timebars_3 = [(345, 350), (370, 390)]
        timebars = [twin_data2d[0][0], twin_data2d[1][0]]
        return timebars

    def plot_additional_ulgdata(self, test_data):
        fnctname = self.plot_additional_ulgdata.__name__
        self.plot_delta_actctrl(fnctname, test_data)
        self.plot_delta_actout(fnctname, test_data)
        self.plot_delta_locpva(fnctname, test_data)
        self.plot_delta_manctrl(fnctname, test_data)
        self.plot_delta_toopca(fnctname, test_data)

    def plot_delta_manctrl(self, fnctname, test_data):
        [csvname, tmcs, manctrl] = self.ulgfile_manual_control_setpoint_0()
        _ = [csvname]
        # https://github.com/PX4/PX4-Autopilot/blob/master/
        # msg/manual_control_setpoint.msg
        man_pitch = manctrl[0]
        man_roll = manctrl[1]
        man_throttle = manctrl[2]
        man_yaw = manctrl[3]
        man_attnorm_arr = Data2D.norm([man_pitch, man_roll], 0, None)
        _ = man_yaw

        print('Plot norm of manctrl')
        ylabel_arr = ['|man att|', '|man throttle|', '||']
        data2d = [man_attnorm_arr,
                  man_throttle,
                  man_throttle * 0]
        self.plot_ax3_using_data2d(tmcs, data2d, ylabel_arr, test_data)
        self.save_plt(fnctname=fnctname, motor1=0, motor2='0_manctrl')

    def plot_delta_actctrl(self, fnctname, test_data):
        [csvname, tac, actctrl] = self.ulgfile_actuator_controls_0_0()
        _ = [csvname]
        act_roll = actctrl[0]
        act_pitch = actctrl[1]
        act_yaw = actctrl[2]
        act_throttle = actctrl[3]
        act_attnorm_arr = Data2D.norm([act_pitch, act_roll], 0, None)
        _ = act_yaw

        print('Plot norm of actctrl')
        ylabel_arr = ['|act att|', '|act throttle|', '||']
        data2d = [act_attnorm_arr,
                  act_throttle,
                  act_throttle * 0]
        self.plot_ax3_using_data2d(tac, data2d, ylabel_arr, test_data)
        self.save_plt(fnctname=fnctname, motor1=0, motor2='0_actctrl')

    def plot_delta_locpva(self, fnctname, test_data):
        [csvname, tvlp, locpva] = self.ulgfile_vehicle_local_position_0()
        _ = [csvname]
        pos = locpva[0:3]
        vel = locpva[3:6]
        acc = locpva[6:9]
        pnorm_arr = Data2D.norm(pos, 0, None)
        vnorm_arr = Data2D.norm(vel, 0, None)
        anorm_arr = Data2D.norm(acc, 0, None)

        print('Plot norm of locpva')
        ylabel_arr = ['|pos|', '|vel|', '|acel|']
        data2d = [pnorm_arr, vnorm_arr, anorm_arr]
        self.plot_ax3_using_data2d(tvlp, data2d, ylabel_arr, test_data)
        self.save_plt(fnctname=fnctname, motor1=0, motor2='0_locpva')

    def plot_delta_actout(self, fnctname, test_data):
        [csvname, tao, actout] = self.ulgfile_actuator_outputs_0()
        _ = [csvname]
        # delta_m1m6 = actout[0] - actout[5]
        # delta_m2m5 = actout[1] - actout[4]
        delta_m3m8 = actout[2] - actout[7]
        delta_m4m7 = actout[3] - actout[6]

        print('Plot delta of actout')
        ylabel_arr = ['$\Delta$ pwm3 - pwm8', '$\Delta$ pwm4 - pwm7', '$\Delta$']
        data2d = [delta_m3m8,
                  delta_m4m7,
                  delta_m4m7 * 0]
        self.plot_ax3_using_data2d(tao, data2d, ylabel_arr, test_data)
        self.save_plt(fnctname=fnctname, motor1=0, motor2='0_actout')

    def plot_delta_toopca(self, fnctname, test_data):
        [csvname, ttc, status, controls, output, pwm_limited] = \
            self.ulgfile_toopazo_ctrlalloc_0()

        # Correct weird values at the end of the flight on controls[2, :]
        controls[2, :][controls[2, :] < -0.5] = 0.0
        # print(controls[2, -500:])

        _ = [csvname, status, pwm_limited]
        # delta_m1m6 = output[0] - output[5]
        # delta_m2m5 = output[1] - output[4]
        delta_m3m8 = output[2] - output[7]
        delta_m4m7 = output[3] - output[6]
        actout_data2d = ArsParser.calculate_ctrlalloc(0.1, controls)
        delta_m4m7_predicted = actout_data2d[3] - actout_data2d[6]

        print('Plot delta of toopca')
        ylabel_arr = ['$\delta$ m3-m8', '$\delta$ m4-m7', 'predicted $\delta$ m4-m7']
        data2d = [delta_m3m8,
                  delta_m4m7,
                  delta_m4m7_predicted]
        self.plot_ax3_using_data2d(ttc, data2d, ylabel_arr, test_data)
        self.save_plt(fnctname=fnctname, motor1=0, motor2='0_toopca')

    @staticmethod
    def calculate_ctrlalloc(d0, actctrl_data2d):
        # Octorotor Coaxial
        # btained from ctrlalloc_octocoax_px4.m
        bmatrix_8pinvn = [
            [-1.4142, +1.4142, +2.0000, +2.0000, +0.4981, +0.0019, -0.0019,
             +0.0019],
            [+1.4142, +1.4142, -2.0000, +2.0000, +0.0019, +0.4981, +0.0019,
             -0.0019],
            [+1.4142, -1.4142, +2.0000, +2.0000, -0.0019, +0.0019, +0.4981,
             +0.0019],
            [-1.4142, -1.4142, -2.0000, +2.0000, +0.0019, -0.0019, +0.0019,
             +0.4981],
            [+1.4142, +1.4142, +2.0000, +2.0000, -0.0019, -0.4981, -0.0019,
             +0.0019],
            [-1.4142, +1.4142, -2.0000, +2.0000, -0.4981, -0.0019, +0.0019,
             -0.0019],
            [-1.4142, -1.4142, +2.0000, +2.0000, -0.0019, +0.0019, -0.0019,
             -0.4981],
            [+1.4142, -1.4142, -2.0000, +2.0000, +0.0019, -0.0019, -0.4981,
             -0.0019]
        ]

        actout_data2d = []
        for samplej in range(0, actctrl_data2d.shape[1]):
            actctrl = actctrl_data2d[:, samplej]
            # print(actctrl)
            # print(actctrl_data2d.shape)
            actout = list(range(0, 8))
            for i in range(0, 8):
                actout[i] = \
                    bmatrix_8pinvn[i][0] * actctrl[0] + \
                    bmatrix_8pinvn[i][1] * actctrl[1] + \
                    bmatrix_8pinvn[i][2] * actctrl[2] + \
                    bmatrix_8pinvn[i][3] * actctrl[3] + \
                    bmatrix_8pinvn[i][4] * d0 + \
                    bmatrix_8pinvn[i][5] * d0 + \
                    bmatrix_8pinvn[i][6] * d0 + \
                    bmatrix_8pinvn[i][7] * d0 + \
                    - 1
            actout_data2d.append(actout)
        actout_data2d = np.array(actout_data2d)
        actout_data2d = np.matrix.transpose(actout_data2d)
        print(actout_data2d.shape)
        return actout_data2d

    @staticmethod
    def estimate_throttle(man_throttle):
        indx = np.argwhere(man_throttle > 0.01)
        nonzero_man_throttle = man_throttle[indx]
        # print('  len(rcval) %s' % len(rcval))
        stats_mode = stats.mode(nonzero_man_throttle)
        mode = stats_mode.mode.flatten()
        count = stats_mode.count.flatten()
        hover_throttle = mode[0]
        return hover_throttle

    def plot_ax3_using_data2d(self, t_arr, data2d, ylabel_arr, test_data):
        # [fig, ax_arr] = FigureTools.create_fig_axes(3, 1)
        fig, ax_arr = plt.subplots(3, 1, figsize=[8, 6])

        xlabel_arr = ['']  # ['Time s']
        y_arr = data2d
        x_arr = [t_arr]
        PlotTools.ax3_x1_y3(ax_arr, x_arr, xlabel_arr, y_arr, ylabel_arr)
        nax = len(ax_arr)
        ax_arr[nax - 1].set(xlabel='Time s')

        # Test that "linalg.norm(vel_arr, axis=0)" does its job
        # i_arr = x_arr[0]
        # vel_arr = [i_arr, i_arr, i_arr]
        # vel_arr = Data2D.to_np_array(vel_arr)
        # test_arr = linalg.norm(vel_arr, axis=0) / np.sqrt(3)
        # ax_arr[0].plot(
        #     x_arr[0], test_arr, color='black', linestyle='dashed')
        # ax_arr[0].set_ylim([i_arr[0], i_arr[-1]])
        # ax_arr[0].set_xlim([i_arr[0], i_arr[-1]])

        self.plot_syndata_add_info(ax_arr, x_arr, y_arr, test_data)

    def save_plt(self, fnctname, motor1, motor2):
        closefig = True
        firstname = self.arsfile_basename + '_' + fnctname
        lastname = '_m%s_m%s' % (motor1, motor2)
        filename = 'plots/' + firstname + lastname
        FigureTools.savefig(filename, closefig)

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
        text_arr, last_ax_total_avg = ArsParser.generate_text_arr(
            ax_arr, x_arr, y_arr, i0, i1)

        # time_arr = x_arr[0]
        x_arr = x_arr[0]
        arsfile = test_data['arsfile']
        ylim_arr = test_data['ylim_arr']
        # units_arr = test_data['units_arr']
        bbox_dict = dict(facecolor='white', edgecolor='none', alpha=0.8)

        if ('test11' in arsfile) or ('test12' in arsfile):
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

        # Add data for coaxial results [(output), throttle, rpm, current]
        #   log_dec22_test12_plot_syndata_m3_m8.png
        #   log_dec22_test12_plot_syndata_m4_m7.png
        c1 = (len(ax_arr) == 3) and (len(y_arr) == 6)
        c2 = (len(ax_arr) == 4) and (len(y_arr) == 8)
        if c1 or c2:
            for indx in range(0, len(ax_arr)):
                ax = ax_arr[indx]
                ylim = ylim_arr[indx]
                arg = text_arr[indx]
                plt.sca(ax)
                x0 = x_arr[i0]  # x_arr[int(i0 * 0.5 + i1 * 0.5)]
                y0 = ylim[0] * 0.95 + ylim[1] * (1 - 0.95)
                ax.text(x0, y0, arg, fontsize=14, color='black', bbox=bbox_dict)

            # Add total current
            indx = len(ax_arr) - 1
            ax = ax_arr[indx]
            ylim = ylim_arr[indx]
            arg = 'tot %s A' % round(float(last_ax_total_avg), 2)
            plt.sca(ax)
            x0 = x_arr[i0]
            y0 = ylim[1] * 0.75
            ax.text(x0, y0, arg, fontsize=14, color='black', bbox=bbox_dict)

    @staticmethod
    def generate_text_arr(ax_arr, x_arr, y_arr, i0, i1):
        # if len(y_arr) != 9:
        #     return
        # else:
        #     [twin, dout_avg, dpwm_avg, drpm_avg, dcur_avg, tcur_avg] = \
        #         ArsParser.calculate_deltas(x_arr, y_arr, i0, i1)
        #     _ = twin
        last_ax_total_avg = None
        _ = x_arr

        text_arr = []
        if (len(ax_arr) == 3) and (len(y_arr) == 6):
            data_m1 = y_arr[0]
            data_m2 = y_arr[3]
            ax0_delta_avg = np.mean(data_m1[i0:i1] - data_m2[i0:i1])  # / twin
            data_m1 = y_arr[1]
            data_m2 = y_arr[4]
            ax1_delta_avg = np.mean(data_m1[i0:i1] - data_m2[i0:i1])  # / twin
            data_m1 = y_arr[2]
            data_m2 = y_arr[5]
            ax2_delta_avg = np.mean(data_m1[i0:i1] - data_m2[i0:i1])  # / twin
            ax2_total_avg = np.mean(data_m1[i0:i1] + data_m2[i0:i1])
            last_ax_total_avg = ax2_total_avg

            # for i in range(0, len(y_arr)):
            #     datai = y_arr[i]
            #     datai = np.array(datai)
            #     nan_indx = np.argwhere(datai is np.nan)
            #     print('nan_indx %s' % nan_indx)
            # # print(np.isnan(y_arr))
            # print('nan_indx %s' % np.argwhere(np.isnan(y_arr)))
            # print(np.array(y_arr).shape)
            # np.nan_to_num(y_arr, copy=False, nan=0.0, posinf=None, neginf=None)
            # print(y_arr[3])
            # print(len(y_arr))

            text_arr = [
                '$\Delta$ %s' % round(float(ax0_delta_avg), 2),
                '$\Delta$ %s rpm' % int(round(float(ax1_delta_avg))),
                '$\Delta$ %s A' % round(float(ax2_delta_avg), 2)
            ]

        if (len(ax_arr) == 4) and (len(y_arr) == 8):
            data_m1 = y_arr[0]
            data_m2 = y_arr[4]
            ax0_delta_avg = np.mean(data_m1[i0:i1] - data_m2[i0:i1])  # / twin
            data_m1 = y_arr[1]
            data_m2 = y_arr[5]
            ax1_delta_avg = np.mean(data_m1[i0:i1] - data_m2[i0:i1])  # / twin
            data_m1 = y_arr[2]
            data_m2 = y_arr[6]
            ax2_delta_avg = np.mean(data_m1[i0:i1] - data_m2[i0:i1])  # / twin
            data_m1 = y_arr[3]
            data_m2 = y_arr[7]
            ax3_delta_avg = np.mean(data_m1[i0:i1] - data_m2[i0:i1])  # / twin
            ax3_total_avg = np.mean(data_m1[i0:i1] + data_m2[i0:i1])
            last_ax_total_avg = ax3_total_avg

            text_arr = [
                '$\Delta$ %s' % round(float(ax0_delta_avg), 2),
                '$\Delta$ %s pwm' % int(round(float(ax1_delta_avg))),
                '$\Delta$ %s rpm' % int(round(float(ax2_delta_avg))),
                '$\Delta$ %s A' % round(float(ax3_delta_avg), 2)
            ]
        return text_arr, last_ax_total_avg

    @staticmethod
    def add_timebars(ax_arr, x_arr, y_arr, i0, i1, test_data, **kwargs):
        ylim_arr = test_data['ylim_arr']
        _ = y_arr

        # time_arr = x_arr[0]
        x_arr = x_arr[0]

        # arsfile = test_data['arsfile']
        # if ('test11' in arsfile) or ('test12' in arsfile):
        #     for axis_indx in range(0, len(ax_arr)):
        #         ax = ax_arr[axis_indx]
        #         ylim = ylim_arr[axis_indx] * 0.9
        #         ymin = ylim[0]
        #         ymax = ylim[1]
        #
        #         x0 = x_arr[i0]
        #         ax.vlines(x=x0, ymin=ymin, ymax=ymax, colors='k',
        #                   linestyles='dashed', label='', **kwargs)
        #         x0 = x_arr[i1]
        #         ax.vlines(x=x0, ymin=ymin, ymax=ymax, colors='k',
        #                   linestyles='dashed', label='', **kwargs)
        #         # return

        selected_axis = len(ax_arr) - 2
        timebars_on_all_axes = True
        for indx in range(0, len(ax_arr)):
            if (not timebars_on_all_axes) and (selected_axis != indx):
                continue
            ax = ax_arr[indx]
            ylim = ylim_arr[indx] * 0.9
            ymin = ylim[0]
            ymax = ylim[1]
            if (len(ax_arr) == 3) and (len(y_arr) == 3):
                data_m1 = y_arr[indx]
                ymin = np.min(data_m1)
                ymax = np.max(data_m1)

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

    warnings.simplefilter('error', UserWarning)

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
        u_arsparser = ArsParser(u_bdir, u_arsfile, u_ulgfile, u_verbose)
        # u_arsparser.plot_basic_ulgdata()
        u_arsparser.plot_mixer_ulgdata()
        u_arsparser.plot_additional_ulgdata(u_test_data)

        # u_test_data['timebars'] = u_arsparser.find_hover_timebars(u_test_data)

        # u_arsparser.calculate_syndata(u_arsparser.rawdata, u_arsoffset)
        u_arsparser.calculate_syndata(u_arsparser.caldata, u_arsoffset)
        # u_arsparser.calculate_syndata(u_arsparser.windata, u_arsoffset)
        u_arsparser.plot_syndata(u_test_data)
        u_arsparser.write_syndata_timebars(u_test_data, u_testkey)
        # u_arsparser.plot_basic_ulgdata()

    if user_args.testall:
        for testi in range(1, 11):
            u_testkey = 'test%s' % testi
            u_test_data = ArsDec22Data.test_db[u_testkey]
            u_bdir = u_test_data['bdir']
            u_arsfile = u_test_data['arsfile']
            u_ulgfile = u_test_data['ulgfile']
            u_arsoffset = u_test_data['arsoffset']

            u_verbose = False
            u_arsparser = ArsParser(u_bdir, u_arsfile, u_ulgfile, u_verbose)
            u_arsparser.plot_basic_ulgdata()
            u_arsparser.plot_mixer_ulgdata()
            u_arsparser.plot_additional_ulgdata(u_test_data)

            # u_test_data['timebars'] = u_arsparser.find_hover_timebars(
            #     u_test_data)
            
            # u_arsparser.calculate_syndata(u_arsparser.rawdata, u_arsoffset)
            u_arsparser.calculate_syndata(u_arsparser.caldata, u_arsoffset)
            # u_arsparser.calculate_syndata(u_arsparser.windata, u_arsoffset)
            u_arsparser.plot_syndata(u_test_data)
            u_arsparser.write_syndata_timebars(u_test_data, u_testkey)

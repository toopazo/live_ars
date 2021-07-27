#!/usr/bin/env python

import numpy as np
from scipy import signal
from scipy import interpolate


class TimeseriesTools:

    @staticmethod
    def test_window(arr, n):
        return np.std(TimeseriesTools.rolling_window(arr, n), 1)

    @staticmethod
    def rolling_window(a, window):
        shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
        strides = a.strides + (a.strides[-1],)
        return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)

    @staticmethod
    def get_window(arr, i, nwindow):
        # size = np.shape(arr)
        # nmax = len(arr) - 1
        ifirst = i
        ilast = i + nwindow
        # if ilast > nmax:
        #     ilast = nmax
        #     sarr = arr[ifirst:ilast]
        # else:
        sarr = arr[ifirst:ilast]
        return sarr

    @staticmethod
    def apply_to_window(arr, fun, nwindow):

        nmax = len(arr) - 1

        # arg = '[apply_to_window] %s' % arr
        # print(arg)
        arg = '[apply_to_window] nwindow %s' % nwindow
        print(arg)
        arg = '[apply_to_window] nmax %s' % nmax
        print(arg)

        ilast = nmax - nwindow + 1
        res_arr = []
        for i in range(0, ilast + 1):
            sarr = TimeseriesTools.get_window(arr, i, nwindow)
            res = fun(sarr)
            res_arr.append(res)
            # arg = '[apply_to_window] ui %s, sarr %s, res %s' % (ui, sarr, res)
            # print(arg)
        return np.array(res_arr)

    @staticmethod
    def add_sarr(sarr):
        return np.sum(sarr)

    @staticmethod
    def add_abs_sarr(sarr):
        return np.std(sarr)

    @staticmethod
    def test_iterate_window():
        marr = np.arange(0, 15)
        mwindow = 5
        TimeseriesTools.apply_to_window(marr, TimeseriesTools.add_sarr, mwindow)

    @staticmethod
    def common_statistics(x_arr, verbose):
        x_arr = np.array(x_arr)
        x_nsamples = len(x_arr)

        # Mean
        x_mean = np.mean(x_arr)
        # Standard deviation
        x_std = np.std(x_arr)
        # Signed deviation
        x_sgndev = x_arr - x_mean
        # Unsigned deviation
        x_usgndev = np.abs(x_sgndev)
        # Mean signed deviation
        x_meansgndev = np.mean(x_sgndev)
        # Max unsigned deviation
        x_maxusgndev = np.max(x_usgndev)
        # Min unsigned deviation
        x_minusgndev = np.min(x_usgndev)

        rdict = {'x_nsamples': x_nsamples,
                 'x_mean': x_mean,
                 'x_std': x_std,
                 'x_meansgndev': x_meansgndev,
                 'x_minusgndev': x_minusgndev,
                 'x_maxusgndev': x_maxusgndev,
                 }

        if verbose:
            for key, value in rdict.items():
                print('[common_statistics] rdict[%s] = %s' % (key, value))

        return rdict

    @staticmethod
    def time_statistics(t_arr, verbose):
        t_arr = np.array(t_arr)
        t_nsamples = len(t_arr)

        # dt = delta times between samples
        t_diff = np.diff(t_arr)
        # Mean
        t_dt_mean = np.mean(t_diff)
        # Standard deviation
        t_dt_std = np.std(t_diff)
        # Signed deviation
        t_dt_sgndev = t_diff - t_dt_mean
        # Unsigned deviation
        t_dt_usgndev = np.abs(t_diff - t_dt_mean)
        # Mean signed deviation
        t_dt_meansgndev = np.mean(t_dt_sgndev)
        # Max unsigned deviation
        t_dt_maxusgndev = np.max(t_dt_usgndev)
        # Min unsigned deviation
        t_dt_minusgndev = np.min(t_dt_usgndev)

        t_start = t_arr[0]
        t_finish = t_arr[-1]
        t_window = t_finish - t_start
        t_dt_ideal = t_window / (t_nsamples - 1)
        t_finish_dt_ideal = t_start + t_dt_ideal * (t_nsamples - 1)
        t_finish_dt_mean = t_start + t_dt_mean * (t_nsamples - 1)
        # t_tferror = (t_start + t_dt_mean * (t_nsamples - 1)) - t_finish

        rdict = {
            't_start': t_start,
            't_finish': t_finish,
            't_nsamples': t_nsamples,
            't_window': t_window,
            't_dt_ideal': t_dt_ideal,
            't_dt_mean': t_dt_mean,
            't_dt_std': t_dt_std,
            't_dt_meansgndev': t_dt_meansgndev,
            't_dt_minusgndev': t_dt_minusgndev,
            't_dt_maxusgndev': t_dt_maxusgndev,
            't_finish_dt_ideal': t_finish_dt_ideal,
            't_finish_dt_mean': t_finish_dt_mean,
        }

        if verbose:
            for key, value in rdict.items():
                print('[time_statistics] rdict[%s] = %s' % (key, value))

        return rdict

    @staticmethod
    def upsample_interp1d(t1_arr, x1_arr, t2_arr, tolkey, tolval, verbose):
        t1_arr = np.array(t1_arr)
        x1_arr = np.array(x1_arr)
        t2_arr = np.array(t2_arr)

        t1_rdict = TimeseriesTools.time_statistics(t1_arr, False)
        t1_nsamples = t1_rdict['t_nsamples']
        # t1_dt_mean = t1_rdict['t_dt_mean']

        t2_rdict = TimeseriesTools.time_statistics(t2_arr, False)
        # t2_nsamples = t2_rdict['t_nsamples']
        # t2_dt_mean = t2_rdict['t_dt_mean']

        x1_nsamples = len(x1_arr)

        if x1_nsamples != t1_nsamples:
            print('[upsample_interp1d] x1_nsamples = %s != t1_nsamples = %s'
                  % (x1_nsamples, t1_nsamples))
            return x1_arr

        if t1_rdict[tolkey] > tolval or t2_rdict[tolkey] > tolval:
            print('[upsample_interp1d] Tolerance error in t1_arr or t2_arr')

            print('[upsample_interp1d] t1_arr:')
            TimeseriesTools.time_statistics(t1_arr, True)

            print('[upsample_interp1d] t2_arr:')
            TimeseriesTools.time_statistics(t2_arr, True)
            return x1_arr

        # Interpolate a 1-D function.
        #
        # x and y are arrays of values used to approximate some function
        # f: y = f(x). This class returns a function whose call method uses
        # interpolation to find the value of new points.

        interp1d_fnct = interpolate.interp1d(x=t1_arr, y=x1_arr)

        # For an ideal signal tf = t0 + dt*(ns-1), then
        # ns = (tf-t0)/dt + 1
        t2_dt_ideal = t2_rdict['t_dt_ideal']
        t1_window = t1_rdict['t_window']
        t1_nsamples_expected = int(round(t1_window / t2_dt_ideal)) + 1
        rt1_arr = np.linspace(t1_arr[0], t1_arr[-1], t1_nsamples_expected)
        rx1_arr = interp1d_fnct(rt1_arr)

        if verbose:
            print('[upsample_interp1d] t1_arr:')
            TimeseriesTools.time_statistics(t1_arr, True)

            print('[upsample_interp1d] x1_arr:')
            print('[upsample_interp1d] x1_nsamples %s' % len(x1_arr))

            print('[upsample_interp1d] t2_arr:')
            TimeseriesTools.time_statistics(t2_arr, True)

            print('[upsample_interp1d] rt1_arr:')
            TimeseriesTools.time_statistics(rt1_arr, True)

            print('[upsample_interp1d] rx1_arr:')
            print('[upsample_interp1d] rx1_nsamples %s' % len(rx1_arr))

        return [rt1_arr, rx1_arr]

    @staticmethod
    def resample(t1_arr, x1_arr, t2_arr, tolkey, tolval, verbose):
        t1_arr = np.array(t1_arr)
        x1_arr = np.array(x1_arr)
        t2_arr = np.array(t2_arr)

        t1_rdict = TimeseriesTools.time_statistics(t1_arr, False)
        t1_nsamples = t1_rdict['t_nsamples']
        # t1_dt_mean = t1_rdict['t_dt_mean']

        t2_rdict = TimeseriesTools.time_statistics(t2_arr, False)
        t2_nsamples = t2_rdict['t_nsamples']
        # t2_dt_mean = t2_rdict['t_dt_mean']

        x1_nsamples = len(x1_arr)

        if x1_nsamples != t1_nsamples:
            print('[resample] t1_arr: x1_nsamples = %s != t1_nsamples = %s'
                  % (x1_nsamples, t1_nsamples))
            return x1_arr

        if t1_rdict[tolkey] > tolval or t2_rdict[tolkey] > tolval:
            print('[resample] Tolerance error in t1_arr or t2_arr')

            print('[resample] t1_arr:')
            TimeseriesTools.time_statistics(t1_arr, True)

            print('[resample] t2_arr:')
            TimeseriesTools.time_statistics(t2_arr, True)
            return x1_arr

        # Resample x to num samples using Fourier method along the given axis.
        # The resampled signal starts at the same value as x but is sampled
        # with a spacing of len(x) / num * (spacing of x). Because a Fourier
        # method is used, the signal is assumed to be periodic.

        # For an ideal signal tf = t0 + dt*(ns-1), then
        # ns = (tf-t0)/dt + 1
        dt = t2_rdict['t_dt_ideal']
        twin = t1_rdict['t_window']
        t1_nsamples_expected = int(round(twin / dt)) + 1

        # rdt = len(x) / num * (spacing of x)
        # rdt = t1_nsamples * t1_dt_ideal * t2_dt_ideal / twin

        # # For a typical .ars (time1) and .ulg (time2) files
        # # scale_factor = 1 / 0.004 = 245.687605706
        # scale_factor = t1_dt_mean / t2_dt_mean
        # # scale_factor = int(round(scale_factor))
        # # Number of samples that t1_arr should have if it were
        # # sampled at the frequency of t2_arr
        # t1_nsamples_expected = scale_factor * t1_nsamples
        # t1_nsamples_expected = int(round(t1_nsamples_expected))

        # x2_arr = signal.resample(x1_arr, t1_nsamples_expected, t=None)
        (rx1_arr, rt1_arr) = \
            signal.resample(x1_arr, t1_nsamples_expected, t=t1_arr)

        _ = t2_nsamples
        # rt1_rdict = TimeseriesTools.time_statistics(rt1_arr, False)
        # rt1_nsamples = rt1_rdict['t_nsamples']
        # if rt1_nsamples != t2_nsamples:
        #     print('[resample] t1_arr: rt1_nsamples = %s != t2_nsamples = %s'
        #           % (rt1_nsamples, t2_nsamples))
        #     return x1_arr

        # t1_finish = t1_rdict['t_finish']
        # t1_finish_dt_ideal = t1_rdict['t_finish_dt_ideal']
        # t1_finish_dt_mean = t1_rdict['t_finish_dt_mean']
        # print('[resample] t1_finish %s' % t1_finish)
        # print('[resample] t1_finish_dt_ideal %s' % t1_finish_dt_ideal)
        # print('[resample] t1_finish_dt_mean %s' % t1_finish_dt_mean)
        #
        # t2_finish = t2_rdict['t_finish']
        # t2_finish_dt_ideal = t2_rdict['t_finish_dt_ideal']
        # t2_finish_dt_mean = t2_rdict['t_finish_dt_mean']
        # print('[resample] t2_finish %s' % t2_finish)
        # print('[resample] t2_finish_dt_ideal %s' % t2_finish_dt_ideal)
        # print('[resample] t2_finish_dt_mean %s' % t2_finish_dt_mean)
        #
        # rt1_rdict = TimeseriesTools.time_statistics(rt1_arr, False)
        #
        # rt1_finish = rt1_rdict['t_finish']
        # rt1_finish_dt_ideal = rt1_rdict['t_finish_dt_ideal']
        # rt1_finish_dt_mean = rt1_rdict['t_finish_dt_mean']
        # print('[resample] rt1_finish %s' % rt1_finish)
        # print('[resample] rt1_finish_dt_ideal %s' % rt1_finish_dt_ideal)
        # print('[resample] rt1_finish_dt_mean %s' % rt1_finish_dt_mean)

        if verbose:
            print('[resample] t1_arr:')
            TimeseriesTools.time_statistics(t1_arr, True)

            print('[resample] x1_arr:')
            print('[resample] x1_nsamples %s' % len(x1_arr))

            print('[resample] t2_arr:')
            TimeseriesTools.time_statistics(t2_arr, True)

            print('[resample] scale_factor %s' % scale_factor)

            print('[resample] rt1_arr:')
            TimeseriesTools.time_statistics(rt1_arr, True)

            print('[resample] rx1_arr:')
            print('[resample] rx1_nsamples %s' % len(rx1_arr))

        return [rt1_arr, rx1_arr]

    @staticmethod
    def closest_element(val, val_arr):
        abs_val_arr = np.abs(val_arr - val)
        indx = abs_val_arr.argmin()
        val_indx = val_arr[indx]
        return indx, val_indx

    @staticmethod
    def elements_satisfying_condition(val_arr, oper, val_c):
        iwin = []
        vwin = []
        iwin_arr = []
        vwin_arr = []
        # oper_is_true = False
        for i in range(0, len(val_arr)):
            val = val_arr[i]
            if oper(val, val_c):
                iwin.append(i)
                vwin.append(val)
                # if not oper_is_true:
                #     print('[] Transition: False to True, val_arr[%s] = %s'
                #           % (i, val))
                #     oper_is_true = True
            else:
                if len(iwin) != 0:
                    iwin_arr.append(iwin)
                    vwin_arr.append(vwin)
                iwin = []
                # if oper_is_true:
                #     print('[] Transition: True to False, val_arr[%s] = %s'
                #           % (i, val))
                #     oper_is_true = False
        if len(iwin) != 0:
            iwin_arr.append(iwin)
            vwin_arr.append(iwin)

        iwin_arr = np.array(iwin_arr, dtype='object')
        vwin_arr = np.array(vwin_arr, dtype='object')
        # iwin_arr = iwin_arr.flatten()

        # for iwin in iwin_arr:
        #     print('  iwin %s' % iwin)
        #     print('val_arr[iwin] %s' % val_arr[iwin])

        return iwin_arr, vwin_arr

    @staticmethod
    def overlapping_time_windows(twin1_arr, twin2_arr, min_delta):
        twin3_arr = []
        for twin1 in twin1_arr:
            # print('  twin1[0] %s, twin1[-1] %s' % (twin1[0], twin1[-1]))
            for twin2 in twin2_arr:
                # print('    twin2[0] %s, twin2[-1] %s' % (twin2[0], twin2[-1]))

                # twin1:   |--------------|
                # twin2:      |--------|
                # twin3:      |--------|
                if (twin2[0] >= twin1[0]) and (twin2[-1] <= twin1[-1]):
                    tstart = twin2[0]
                    tfinish = twin2[-1]
                    delta = tfinish - tstart
                    if delta >= min_delta:
                        # print('    Full match: tstart %s tfinish %s delta %s'
                        #       % (tstart, tfinish, round(delta, 2)))
                        twin3_arr.append((tstart, tfinish))
                    continue

                # twin1:   |--------------|
                # twin2:      |--------------|
                # twin3:      |-----------|
                if (twin2[0] >= twin1[0]) \
                        and (twin2[-1] > twin1[-1]) \
                        and (twin2[0] < twin1[-1]):
                    tstart = twin2[0]
                    tfinish = twin1[-1]
                    delta = tfinish - tstart
                    if delta >= min_delta:
                        # print('    Semi match: tstart %s tfinish %s delta %s'
                        #       % (tstart, tfinish, round(delta, 2)))
                        twin3_arr.append((tstart, tfinish))
                    continue

                # twin1:      |--------------|
                # twin2:   |--------------|
                # twin3:      |-----------|
                if (twin2[0] < twin1[0]) \
                        and (twin2[-1] > twin1[0]) \
                        and (twin2[-1] <= twin1[-1]):
                    tstart = twin1[0]
                    tfinish = twin2[-1]
                    delta = tfinish - tstart
                    if delta >= min_delta:
                        # print('    Semi match: tstart %s tfinish %s delta %s'
                        #       % (tstart, tfinish, round(delta, 2)))
                        twin3_arr.append((tstart, tfinish))
                    continue
        # print('    twin3_arr %s' % twin3_arr)
        return twin3_arr


if __name__ == '__main__':
    TimeseriesTools.test_iterate_window()

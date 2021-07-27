
import numpy as np
from numpy import linalg
# from time_series import TimeseriesTools
from toopazo_tools.time_series import TimeseriesTools


class Data2D:
    @staticmethod
    def to_np_array(data2d):
        data2d = np.array(data2d)
        dshape = data2d.shape
        if len(dshape) != 2:
            print('[to_np_array] dshape != 2')
            # raise RuntimeError
            return None
        # else:
        #     nvariables = dshape[0]
        #     nsamples = dshape[1]
        return data2d

    @staticmethod
    def subgroup(data2d, indx):
        return data2d[indx]

    @staticmethod
    def norm(data2d, i0, i1):
        n = linalg.norm(data2d[i0:i1], axis=0)
        return n

    @staticmethod
    def upsample_data2d(data2d_time, data2d, new_time, tolkey, tolval):
        dshape = data2d.shape
        if len(dshape) != 2:
            print('[resample_data2d] dshape != 2')
            return None
        else:
            nvariables = dshape[0]
            nsamples = dshape[1]
            _ = nsamples

        verbose = False
        new_data2d = []
        new_data2d_time = []
        prev_rt1_arr = []
        for i in range(0, nvariables):
            data_arr = data2d[i]
            # [rt1_arr, rx1_arr] = TimeseriesTools.resample(
            [rt1_arr, rx1_arr] = TimeseriesTools.upsample_interp1d(
                data2d_time, data_arr, new_time, tolkey, tolval, verbose)
            if (len(prev_rt1_arr) != 0) and (len(rt1_arr) != len(prev_rt1_arr)):
                print('[resample_data2d] len(rt1_arr) != len(prev_rt1_arr)')
                print('[resample_data2d] len(rt1_arr) %s, len(prev_rt1_arr) %s'
                      % (len(rt1_arr), len(prev_rt1_arr)))
                return None
            else:
                prev_rt1_arr = rt1_arr
            new_data2d_time.append(rt1_arr)
            new_data2d.append(rx1_arr)

        # rt1_arr are all the same, so pick the first one
        new_data2d_time = new_data2d_time[0]

        return new_data2d_time, Data2D.to_np_array(new_data2d)

    @staticmethod
    def search_and_replace_nan(data2d, maxnum_nan):
        dshape = data2d.shape
        if len(dshape) != 2:
            print('[search_and_replace_nan] dshape != 2')
            return None
        else:
            nvariables = dshape[0]
            nsamples = dshape[1]
            _ = nsamples

        # Correct for NaN in data_matrix
        # data2d = [data1_arr, data2_arr, .. , datan_arr]

        for i in range(0, nvariables):
            datai_arr = data2d[i]
            indx_nan = np.argwhere(np.isnan(datai_arr))
            num_nan = len(indx_nan)
            if num_nan <= maxnum_nan:
                # Assign previous value
                datai_arr[indx_nan] = datai_arr[indx_nan - 1]
            else:
                print('[search_and_replace_nan] Too many NaN in data2d[%s]' % i)
                print('[search_and_replace_nan] num_nan %s' % num_nan)
                # raise RuntimeError
                return None

        return data2d

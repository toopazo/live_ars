#!/usr/bin/env python

from toopazo_tools.file_folder import FileFolderTools
import numpy as np
import matplotlib.pyplot as plt
import pickle
import copy
import matplotlib
matplotlib.rcParams.update({'font.size': 18})


class ArsDec22Data:
    bdir = '/home/tzo4/Dropbox/tomas/pennState/avia/firefly_logBook/' \
           '2020-12-22_firefly_mixer'
    test_db = {}

    testkey = 'test1'
    arsfile = bdir + '/' + 'logs/log_dec22_test1.ars'
    ulgfile = bdir + '/' + 'logs/log_140_2020-12-22-13-32-38.ulg'
    # ylim_arr = np.array([[-1.0, 0.5], [900, 1700], [0, 3500], [0, 10]])
    # units_arr = ['', 'pwm', 'rpm', 'A']
    ylim_arr = np.array([[0, 1], [0, 3500], [0, 10]])
    units_arr = ['', 'rpm', 'A']
    arsoffset = 28200
    # timebars_1 = [(2700, 4000), (8600, 15400)]
    # timebars_2 = [(2700, 4000), (9000, 11000)]
    # timebars_3 = [(343, 348), (370, 378)]
    timebars_4 = [(345, 348), (388, 391)]
    test_db[testkey] = {
        'bdir': bdir,
        'arsfile': arsfile,
        'ulgfile': ulgfile,
        'ylim_arr': ylim_arr,
        'units_arr': units_arr,
        'arsoffset': arsoffset,
        'timebars': timebars_4
    }

    testkey = 'test2'
    arsfile = bdir + '/' + 'logs/log_dec22_test2.ars'
    ulgfile = bdir + '/' + 'logs/log_141_2020-12-22-13-41-26.ulg'
    # ylim_arr = np.array([[-1.0, 0.5], [900, 1700], [0, 3500], [0, 10]])
    # units_arr = ['', 'pwm', 'rpm', 'A']
    ylim_arr = np.array([[0, 1], [0, 3500], [0, 10]])
    units_arr = ['', 'rpm', 'A']
    arsoffset = 20400
    # timebars_1 = [(2800, 5100), (9100, 15000)]
    # timebars_2 = [(4000, 5000), (13200, 15000)]
    # timebars_3 = [(110, 114), (143, 148)]
    timebars_4 = [(116, 119), (155, 158)]
    test_db[testkey] = {
        'bdir': bdir,
        'arsfile': arsfile,
        'ulgfile': ulgfile,
        'ylim_arr': ylim_arr,
        'units_arr': units_arr,
        'arsoffset': arsoffset,
        'timebars': timebars_4
    }

    testkey = 'test3'
    arsfile = bdir + '/' + 'logs/log_dec22_test3.ars'
    ulgfile = bdir + '/' + 'logs/log_142_2020-12-22-13-51-38.ulg'
    # ylim_arr = np.array([[-1.0, 0.5], [900, 1700], [0, 3500], [0, 10]])
    # units_arr = ['', 'pwm', 'rpm', 'A']
    ylim_arr = np.array([[0, 1], [0, 3500], [0, 10]])
    units_arr = ['', 'rpm', 'A']
    arsoffset = 23300
    # timebars_1 = [(2500, 5500), (9300, 15600)]
    # timebars_2 = [(4000, 5500), (14000, 15600)]
    # timebars_3 = [(90, 95), (125, 130)]
    timebars_4 = [(92, 95), (135, 138)]
    test_db[testkey] = {
        'bdir': bdir,
        'arsfile': arsfile,
        'ulgfile': ulgfile,
        'ylim_arr': ylim_arr,
        'units_arr': units_arr,
        'arsoffset': arsoffset,
        'timebars': timebars_4
    }

    testkey = 'test4'
    arsfile = bdir + '/' + 'logs/log_dec22_test4.ars'
    ulgfile = bdir + '/' + 'logs/log_143_2020-12-22-13-58-18.ulg'
    # ylim_arr = np.array([[-1.0, 0.5], [900, 1700], [0, 3500], [0, 10]])
    # units_arr = ['', 'pwm', 'rpm', 'A']
    ylim_arr = np.array([[0, 1], [0, 3500], [0, 10]])
    units_arr = ['', 'rpm', 'A']
    arsoffset = 20500
    # timebars_1 = [(2700, 5500), (11000, 20000)]
    # timebars_2 = [(4000, 5600), (16000, 18000)]
    timebars_4 = [(142, 145), (200, 203)]
    test_db[testkey] = {
        'bdir': bdir,
        'arsfile': arsfile,
        'ulgfile': ulgfile,
        'ylim_arr': ylim_arr,
        'units_arr': units_arr,
        'arsoffset': arsoffset,
        'timebars': timebars_4
    }

    testkey = 'test5'
    arsfile = bdir + '/' + 'logs/log_dec22_test5.ars'
    ulgfile = bdir + '/' + 'logs/log_144_2020-12-22-14-03-44.ulg'
    # ylim_arr = np.array([[-1.0, 0.5], [900, 1700], [0, 3500], [0, 10]])
    # units_arr = ['', 'pwm', 'rpm', 'A']
    ylim_arr = np.array([[0, 1], [0, 3500], [0, 10]])
    units_arr = ['', 'rpm', 'A']
    arsoffset = 11100
    # timebars_1 = [(2200, 3700), (9200, 13300)]
    # timebars_2 = [(2200, 3200), (11600, 13300)]
    timebars_4 = [(85, 88), (124, 127)]
    test_db[testkey] = {
        'bdir': bdir,
        'arsfile': arsfile,
        'ulgfile': ulgfile,
        'ylim_arr': ylim_arr,
        'units_arr': units_arr,
        'arsoffset': arsoffset,
        'timebars': timebars_4
    }

    testkey = 'test6'
    arsfile = bdir + '/' + 'logs/log_dec22_test6.ars'
    ulgfile = bdir + '/' + 'logs/log_146_2020-12-22-14-20-12.ulg'
    # ylim_arr = np.array([[-1.0, 0.5], [900, 1700], [0, 3500], [0, 10]])
    # units_arr = ['', 'pwm', 'rpm', 'A']
    ylim_arr = np.array([[0, 1], [0, 3500], [0, 10]])
    units_arr = ['', 'rpm', 'A']
    arsoffset = 68300
    # timebars_1 = [(2700, 8000), (13000, 19000)]
    # timebars_2 = [(4100, 5700), (16200, 17800)]
    timebars_4 = [(520, 523), (566, 569)]
    test_db[testkey] = {
        'bdir': bdir,
        'arsfile': arsfile,
        'ulgfile': ulgfile,
        'ylim_arr': ylim_arr,
        'units_arr': units_arr,
        'arsoffset': arsoffset,
        'timebars': timebars_4
    }
    testkey = 'test7'
    arsfile = bdir + '/' + 'logs/log_dec22_test7.ars'
    ulgfile = bdir + '/' + 'logs/log_147_2020-12-22-14-27-20.ulg'
    # ylim_arr = np.array([[-1.0, 0.5], [900, 1700], [0, 3500], [0, 10]])
    # units_arr = ['', 'pwm', 'rpm', 'A']
    ylim_arr = np.array([[0, 1], [0, 3500], [0, 10]])
    units_arr = ['', 'rpm', 'A']
    arsoffset = 15000
    # timebars_1 = [(2700, 5500), (11000, 19700)]
    # timebars_2 = [(3800, 5000), (16000, 18000)]
    timebars_4 = [(99, 102), (160, 163)]
    test_db[testkey] = {
        'bdir': bdir,
        'arsfile': arsfile,
        'ulgfile': ulgfile,
        'ylim_arr': ylim_arr,
        'units_arr': units_arr,
        'arsoffset': arsoffset,
        'timebars': timebars_4
    }

    testkey = 'test8'
    arsfile = bdir + '/' + 'logs/log_dec22_test8.ars'
    ulgfile = bdir + '/' + 'logs/log_148_2020-12-22-14-34-10.ulg'
    # ylim_arr = np.array([[-1.0, 0.5], [900, 1700], [0, 3500], [0, 10]])
    # units_arr = ['', 'pwm', 'rpm', 'A']
    ylim_arr = np.array([[0, 1], [0, 3500], [0, 10]])
    units_arr = ['', 'rpm', 'A']
    arsoffset = 41600
    # timebars_1 = [(2700, 6000), (10000, 21000)]
    # timebars_2 = [(4000, 5300), (18000, 20000)]
    timebars_4 = [(214, 217), (277, 280)]
    test_db[testkey] = {
        'bdir': bdir,
        'arsfile': arsfile,
        'ulgfile': ulgfile,
        'ylim_arr': ylim_arr,
        'units_arr': units_arr,
        'arsoffset': arsoffset,
        'timebars': timebars_4
    }

    testkey = 'test9'
    arsfile = bdir + '/' + 'logs/log_dec22_test9.ars'
    ulgfile = bdir + '/' + 'logs/log_149_2020-12-22-14-41-30.ulg'
    # ylim_arr = np.array([[-1.0, 0.5], [900, 1700], [0, 3500], [0, 10]])
    # units_arr = ['', 'pwm', 'rpm', 'A']
    ylim_arr = np.array([[0, 1], [0, 3500], [0, 10]])
    units_arr = ['', 'rpm', 'A']
    arsoffset = 24500
    # timebars_1 = [(2700, 5000), (10000, 18000)]
    # timebars_2 = [(3200, 4700), (15000, 17000)]
    timebars_4 = [(136, 139), (195, 198)]
    test_db[testkey] = {
        'bdir': bdir,
        'arsfile': arsfile,
        'ulgfile': ulgfile,
        'ylim_arr': ylim_arr,
        'units_arr': units_arr,
        'arsoffset': arsoffset,
        'timebars': timebars_4
    }

    testkey = 'test10'
    arsfile = bdir + '/' + 'logs/log_dec22_test10.ars'
    ulgfile = bdir + '/' + 'logs/log_150_2020-12-22-14-48-52.ulg'
    # ylim_arr = np.array([[-1.0, 0.5], [900, 1700], [0, 3500], [0, 10]])
    # units_arr = ['', 'pwm', 'rpm', 'A']
    ylim_arr = np.array([[0, 1], [0, 3500], [0, 10]])
    units_arr = ['', 'rpm', 'A']
    arsoffset = 11200
    # timebars_1 = [(2700, 6500), (12000, 24000)]
    # timebars_2 = [(5200, 6700), (17000, 20000)]
    timebars_4 = [(110, 113), (184, 187)]
    test_db[testkey] = {
        'bdir': bdir,
        'arsfile': arsfile,
        'ulgfile': ulgfile,
        'ylim_arr': ylim_arr,
        'units_arr': units_arr,
        'arsoffset': arsoffset,
        'timebars': timebars_4
    }

    testkey = 'test11'
    arsfile = bdir + '/' + 'logs/log_dec22_test11.ars'
    ulgfile = bdir + '/' + 'logs/log_151_2020-12-22-14-51-40.ulg'
    # ylim_arr = np.array([[-1.0, 0.5], [1000, 2000], [0, 3500], [0, 10]])
    # units_arr = ['', 'pwm', 'rpm', 'A']
    ylim_arr = np.array([[0, 1], [0, 3500], [0, 10]])
    units_arr = ['', 'rpm', 'A']
    xlim_arr = np.array([340, 370])
    # According to xcorr_dict arsoffset should be 19500,
    # but visually arsoffset equals to 18500 gives a better result
    arsoffset = 18500
    # timebars_1 = [(4000, 5000), (6300, 7100)]
    # timebars_2 = [(4000, 5000), (6300, 7100)]
    # timebars_3 = [(353, 356), (363, 366)]
    timebars_4 = [(355, 358), (364, 367)]
    # text_xy0 = [(0.3, -0.8), (0.3, 1150), (0.3, 500), (0.3, 1.1)]
    text_xy0 = [(0.3, -0.8), (0.3, 500), (0.3, 1.1)]
    # transition = {'x0': 360.5, 'y0': 0.1, 'x1': 362, 'y1': 0.5}
    transition = {'x0': 360.5, 'y0': 0.6, 'x1': 362, 'y1': 0.9}
    test_db[testkey] = {
        'bdir': bdir,
        'arsfile': arsfile,
        'ulgfile': ulgfile,
        'ylim_arr': ylim_arr,
        'units_arr': units_arr,
        'xlim_arr': xlim_arr,
        'arsoffset': arsoffset,
        'timebars': timebars_4,
        'text_xy0': text_xy0,
        'transition': transition
    }

    testkey = 'test12'
    arsfile = bdir + '/' + 'logs/log_dec22_test12.ars'
    ulgfile = bdir + '/' + 'logs/log_152_2020-12-22-14-58-22.ulg'
    # ylim_arr = np.array([[-1.0, 0.5], [1000, 2000], [0, 3500], [0, 10]])
    # units_arr = ['', 'pwm', 'rpm', 'A']
    ylim_arr = np.array([[0, 1], [0, 3500], [0, 10]])
    units_arr = ['', 'rpm', 'A']
    xlim_arr = np.array([70, 100])
    arsoffset = 19500
    # timebars_1 = [(4200, 4900), (5800, 6200)]
    # timebars_2 = [(4200, 4900), (5800, 6200)]
    # timebars_3 = [(86, 89), (92, 95)]
    timebars_4 = [(86, 89), (92, 95)]
    # text_xy0 = [(0.3, -0.8), (0.3, 1150), (0.3, 500), (0.3, 1.1)]
    text_xy0 = [(0.3, -0.8), (0.3, 500), (0.3, 1.1)]
    # transition = {'x0': 91.5, 'y0': 0.1, 'x1': 92.5, 'y1': 0.7}
    transition = {'x0': 91.5, 'y0': 0.6, 'x1': 92.5, 'y1': 0.9}
    test_db[testkey] = {
        'bdir': bdir,
        'arsfile': arsfile,
        'ulgfile': ulgfile,
        'ylim_arr': ylim_arr,
        'units_arr': units_arr,
        'xlim_arr': xlim_arr,
        'arsoffset': arsoffset,
        'timebars': timebars_4,
        'text_xy0': text_xy0,
        'transition': transition
    }

    # Let us check the data integrity
    for key, value in test_db.items():
        # print('test_db[%s] = %s' % (key, value))
        testkey = key
        arsfile = value['arsfile']
        ulgfile = value['ulgfile']
        if not FileFolderTools.is_file(arsfile):
            arg = '[test_db] Error in %s, arsfile %s is not a file' \
                  % (testkey, arsfile)
            raise RuntimeError(arg)

        if not FileFolderTools.is_file(ulgfile):
            arg = '[test_db] Error in %s, ulgfile %s is not a file' \
                  % (testkey, ulgfile)
            raise RuntimeError(arg)

        # if verbose:
        #     arg = '[test_db] test_db[%s] = (%s, %s)' \
        #           % (u_testkey, arsfile, ulgfile)
        #     print(arg)

    # return test_db


class ArsDec22DataSummary:
    # indx_arr = list(range(0, 22))
    name_arr = [
        'status_mean',       # 0
        'status_std',  # 0

        'outa_mean',    # 0
        'outa_std',     # 1
        'pwma_mean',    # 2
        'pwma_std',     # 3
        'rpma_mean',    # 4
        'rpma_std',     # 5
        'cura_mean',    # 6
        'cura_std',     # 7

        'outb_mean',    # 8
        'outb_std',     # 9
        'pwmb_mean',    # 10
        'pwmb_std',     # 11
        'rpmb_mean',    # 12
        'rpmb_std',     # 13
        'curb_mean',    # 14
        'curb_std',     # 15

        'twin',         # 16
        'dout_avg',     # 17
        'dpwm_avg',     # 18
        'drpm_avg',     # 19
        'dcur_avg',     # 20
        'tcur_avg',     # 21
    ]

    @staticmethod
    def indx_to_name(indx):
        name_arr = ArsDec22DataSummary.name_arr
        # indx_arr = ArsDec22DataSummary.indx_arr
        # return name_arr[indx_arr.index(indx)]
        return name_arr[indx]

    @staticmethod
    def name_to_indx(name):
        name_arr = ArsDec22DataSummary.name_arr
        # indx_arr = ArsDec22DataSummary.indx_arr
        # indx = indx_arr[name_arr.index(name)]
        return name_arr.index(name)

    @staticmethod
    def pkl_parser(filename):
        # fpath = ArsDec22Data.bdir + '/plots/' + filename
        with open(filename, 'rb') as fd:
            syndata_timebars_arr = pickle.load(fd)

        # print('[pkl_parser] syndata_timebars_arr = %s' % syndata_timebars_arr)
        # syndata_timebars_arr = [
        #     ['m3_m8', 1, array([1., 1., 1., ..., 1., 1., 1.]),
        #      -0.0882059189668421, 0.03838717367634933, 1472.9105263157894,
        #      16.799840059916676, 2325.126402866639, 44.27566360245065,
        #      4.270351017323926, 0.2080924700333582, -0.02103710931736842,
        #      0.04599149963047344, 1502.2876315789474, 20.118926796507143,
        #      2485.113279039361, 78.87168390542264, 6.062992790404577,
        #      0.25131301196702205, 15.472808999999998, -0.06716880964947368,
        #      -29.377105263157894, -159.98687617272094, -1.7926417730806505,
        #      10.333343807728502],
        #     ['m3_m8', 2, array([1., 1., 1., ..., 1., 1., 1.]),
        #      -0.34152177475000006, 0.029401990154092388, 1362.08475,
        #      12.870019454951626, 1733.5084906339353, 28.829467676375685,
        #      1.722287018529197, 0.11696343781902527, 0.20697626401666666,
        #      0.034883904050819606, 1602.0490833333333, 15.261367593580495,
        #      2883.9780651814094, 45.90047350016069, 10.34559839403661,
        #      0.4188086490211618, 48.80160999999998, -0.5484980387666667,
        #      -239.96433333333334, -1150.4695745474737, -8.623311375507415,
        #      12.067885412565806],
        #     ['m4_m7', 1, array([1., 1., 1., ..., 1., 1., 1.]),
        #      -0.004019265490792105, 0.041753504115524774, 1509.7452631578947,
        #      18.27193285325627, 2488.612999854334, 58.18630131242202,
        #      6.23555728983876, 0.35169396092754346, -0.0711880771388421,
        #      0.03695469614488976, 1480.3513157894736, 16.164564830623647,
        #      2370.075715852477, 49.06430528578121, 4.279812568633891,
        #      0.11942946522283147, 15.472808999999998, 0.06716881164805,
        #      29.393947368421053, 118.53728400185632, 1.9557447212048689,
        #      10.515369858472653],
        #     ['m4_m7', 2, array([1., 1., 1., ..., 1., 1., 1.]),
        #      -0.18294876591666664, 0.028391192700220197, 1431.4633333333334,
        #      12.425229262360602, 2077.443238239453, 21.666015265698267,
        #      3.634622335322449, 0.280078953035325, 0.06855320765683334,
        #      0.023528350405597774, 1541.49125, 10.301088458871712,
        #      2580.565467262572, 74.98522559451798, 6.266501355014678,
        #      0.19086265815462908, 48.80160999999998, -0.25150197357349996,
        #      -110.02791666666667, -503.1222290231188, -2.63187901969223,
        #      9.901123690337126]
        # ]

        testdict = {}
        for syndata_timebars in syndata_timebars_arr:
            # [
            #     key, cnt,
            #     status,
            #     outa_mean, outa_std, pwma_mean, pwma_std,
            #     rpma_mean, rpma_std, cura_mean, cura_std,
            #     outb_mean, outb_std, pwmb_mean, pwmb_std,
            #     rpmb_mean, rpmb_std, curb_mean, curb_std,
            #     twin, dout_avg, dpwm_avg, drpm_avg, dcur_avg, tcur_avg
            # ] = syndata_timebars
            key = syndata_timebars.pop(0)
            cnt = syndata_timebars.pop(0)

            # testkey = m3_m8_1, m3_m8_2, m4_m7_1, m4_m7_2
            testkey = '%s_%s' % (key, cnt)
            testvalue = {}
            for name in ArsDec22DataSummary.name_arr:
                indx = ArsDec22DataSummary.name_to_indx(name)
                data = syndata_timebars[indx]
                testvalue[name] = data

            testdict[testkey] = testvalue
        return testdict

    @staticmethod
    def load_pkl_files(test_file_arr):
        # dec22dict= {'m3_m8_1': {'outa_mean': outa_mean_arr,
        # .. , 'tcur_avg': tcur_avg_arr}}
        emtpy_testdict = {}
        name_arr = ArsDec22DataSummary.name_arr
        for indx in range(0, len(name_arr)):
            testkey = ArsDec22DataSummary.indx_to_name(indx)
            testvalue = np.nan
            emtpy_testdict[testkey] = testvalue

        # testkey = m3_m8_1, m3_m8_2, m4_m7_1, m4_m7_2

        dec22dict = {}
        for testfile in test_file_arr:
            fpath = ArsDec22Data.bdir + '/plots/' + testfile
            testdict = ArsDec22DataSummary.pkl_parser(fpath)

            # Initialize vardict
            if not list(testdict.keys())[0] in dec22dict:
                for testkey in testdict.keys():
                    dec22dict[testkey] = copy.deepcopy(emtpy_testdict)

            # Append testdict to dec22dict
            for testkey, testvalue in testdict.items():
                for name, data in testvalue.items():
                    if dec22dict[testkey][name] is np.nan:
                        dec22dict[testkey][name] = np.array([data])
                    else:
                        dec22dict[testkey][name] = \
                            np.hstack([dec22dict[testkey][name], np.array(data)])

        # dec22dict = ArsDec22DataSummary.dict_info(dec22dict)
        return dec22dict

    @staticmethod
    def dict_info(mdict, d=''):
        # dec22dict= {'m3_m8_1': {'outa_mean': outa_mean_arr,
        # .. , 'tcur_avg': tcur_avg_arr}}
        for key, value in mdict.items():
            tvalue = type(value)
            # print('[dict_info] key %s, type(value) %s' % (key, tvalue))
            if tvalue is dict:
                print('[dict_info] %s key %s is dict' % (d, key))
                mdict[key] = ArsDec22DataSummary.dict_info(value, d=(d+'  '))
            else:
                if tvalue is np.ndarray:
                    print('[dict_info] %s key %s is np.ndarray with shape %s'
                          % (d, key, value.shape))
                else:
                    print('[dict_info] %s type(value) shape %s' % (d, tvalue))

        return mdict

    @staticmethod
    def polyfit(x_arr, y_arr, deg):
        # polynomial fit, p(x) = p[0] * x**deg + ... + p[deg]
        i_arr = np.argsort(x_arr)
        x_arr = x_arr[i_arr]
        y_arr = y_arr[i_arr]
        pol = np.poly1d(np.polyfit(x_arr, y_arr, deg=deg))
        # print(model)
        p_arr = []
        x_arr = np.linspace(0.8, 1.4, 100)
        for i in range(0, len(x_arr)):
            x = x_arr[i]
            p_arr.append(pol(x))

        return [x_arr, p_arr, pol]

    @staticmethod
    def plot(motor1, motor2, test_file_arr, filename):
        fig, ax_arr = plt.subplots(2, 1, figsize=[8, 6])

        mx_my = "m%s_m%s" % (motor1, motor2)
        print('[plot] mx_my %s' % mx_my)
        # fig.suptitle('Average hover performance: %s' % mx_my)
        # fig.suptitle('Coaxial rotor: Mean hover performance '
        #              'at different speed ratios $\eta_\Omega$')

        bbox_dict = dict(facecolor='white', edgecolor='none', alpha=0.8)

        dec22_dict = ArsDec22DataSummary.load_pkl_files(test_file_arr)
        # dec22dict = ArsDec22DataSummary.dict_info(dec22dict)

        include_default = True

        mx_my_custom = '%s_2' % mx_my
        ed_dict = dec22_dict[mx_my_custom]
        # drpm_avg = ed_dict['drpm_avg']
        custom_dcur_avg = ed_dict['dcur_avg']
        custom_tcur_avg = ed_dict['tcur_avg']
        custom_eta_u = ed_dict['rpma_mean']
        custom_eta_l = ed_dict['rpmb_mean']
        custom_eta_rpm = np.array(custom_eta_u) / np.array(custom_eta_l)

        mx_my_default = '%s_1' % mx_my
        ed_dict = dec22_dict[mx_my_default]
        # drpm_avg = ed_dict['drpm_avg']
        default_dcur_avg = ed_dict['dcur_avg']
        default_tcur_avg = ed_dict['tcur_avg']
        default_eta_u = ed_dict['rpma_mean']
        default_eta_l = ed_dict['rpmb_mean']
        default_eta_rpm = np.array(default_eta_u) / np.array(default_eta_l)

        mc = 'red'  # 'green'
        ax_arr[0].scatter(custom_eta_rpm, custom_tcur_avg, color=mc)
        ax_arr[1].scatter(custom_eta_rpm, custom_dcur_avg, color=mc)

        if include_default:
            mc = 'red'
            ax_arr[0].scatter(default_eta_rpm, default_tcur_avg, color=mc)
            ax_arr[1].scatter(default_eta_rpm, default_dcur_avg, color=mc)

        # Set lebels
        ax_arr[0].grid(True)
        ax_arr[0].set(xlabel='',
                      ylabel='Total current, A')
        ax_arr[1].grid(True)
        ax_arr[1].set(xlabel='Rotor speed ratio $\eta_{\Omega}$',
                      ylabel='$\Delta$ current, A')

        # polynomial fit to total current
        if include_default:
            x_arr = np.hstack((default_eta_rpm, custom_eta_rpm))
            y_arr = np.hstack((default_tcur_avg, custom_tcur_avg))
        else:
            x_arr = custom_eta_rpm
            y_arr = custom_tcur_avg
        [x_arr, p_arr, pol] = ArsDec22DataSummary.polyfit(x_arr, y_arr, 2)
        # print(np.argwhere(np.array(x_arr) == 1)[0][0])
        print('[plot] p_arr[np.argwhere(np.array(x_arr) == 1)] %s'
              % p_arr[np.argwhere(np.array(x_arr) == 1)[0][0]])
        print('[plot] x_arr[np.argwhere(np.array(x_arr) == 1)] %s'
              % x_arr[np.argwhere(np.array(x_arr) == 1)[0][0]])
        # print(np.argmin(np.array(p_arr)))
        print('[plot] p_arr[np.argmin(np.array(p_arr))] %s'
              % p_arr[np.argmin(np.array(p_arr))])
        # print(np.argmin(np.array(p_arr)))
        print('[plot] x_arr[np.argmin(np.array(p_arr))] %s'
              % x_arr[np.argmin(np.array(p_arr))])

        x0 = np.real(pol.roots[0])
        print('[plot] total current pol(%s) %s, pol(1) %s'
              % (x0, pol(x0), pol(1)))
        psav = (pol(1)-pol(x0))/pol(1)*100
        print('[plot] total power saving %s' % psav)

        ax = ax_arr[0]
        arg = 'Minimum current at $\eta_{\Omega}$ %s' % round(x0, 2)
        ymin = 2
        ymax = 12
        ArsDec22DataSummary.add_polyfit_to_subplot(
            ax, x_arr, p_arr, pol, arg, ymin, ymax)

        # polynomial fit to delta current
        if include_default:
            x_arr = np.hstack((default_eta_rpm, custom_eta_rpm))
            y_arr = np.hstack((default_dcur_avg, custom_dcur_avg))
        else:
            x_arr = custom_eta_rpm
            y_arr = custom_dcur_avg
        [x_arr, p_arr, pol] = ArsDec22DataSummary.polyfit(x_arr, y_arr, 1)

        x0 = np.real(pol.roots[0])
        print('[plot] delta current pol(%s) %s, pol(1) %s'
              % (x0, pol(x0), pol(1)))

        ax = ax_arr[1]
        arg = 'Equal torque at $\eta_{\Omega}$ %s' % round(x0, 2)
        ymin = -5
        ymax = +5
        ArsDec22DataSummary.add_polyfit_to_subplot(
            ax, x_arr, p_arr, pol, arg, ymin, ymax)

        # Limit axis
        if mx_my == 'm4_m7':
            xlim_arr = [0.4, 1.6]
            ax_arr[0].set_xlim(xlim_arr)
            ax_arr[0].set_ylim([0, 15])
            ax_arr[0].axes.xaxis.set_ticklabels([])
            ax_arr[1].set_xlim(xlim_arr)
            ax_arr[1].set_ylim([-8, 8])
        else:
            xlim_arr = [0.4, 1.6]
            ax_arr[0].set_xlim(xlim_arr)
            ax_arr[0].set_ylim([0, 15])
            ax_arr[0].axes.xaxis.set_ticklabels([])
            ax_arr[1].set_xlim(xlim_arr)
            ax_arr[1].set_ylim([-10, 10])

        jpgfile = '/home/tzo4/Dropbox/tomas/pennState/avia/' \
                  'firefly_logBook/2020-12-22_firefly_mixer/plots/' + filename
        print('[plot] saving filename %s' % filename)
        plt.savefig(jpgfile)

    @staticmethod
    def add_polyfit_to_subplot(ax, x_arr, p_arr, pol, arg, ymin, ymax):
        ax.plot(x_arr, p_arr, color='black')
        # ax_arr[0].text(1, 5, str(pol.roots))
        x0 = round(np.real(pol.roots[0]), 2)
        ax.vlines(x=x0, ymin=ymin, ymax=ymax, colors='k', linestyles='dashed')
        # arg = 'Minimum current at $\eta_{\Omega}$ %s' % x0
        bbox_dict = dict(facecolor='white', edgecolor='none', alpha=0.8)
        ax.text(x0+0.05, ymin, arg, bbox=bbox_dict)

    @staticmethod
    def eta_delta_equiv():
        fig, ax_arr = plt.subplots(2, 1, figsize=[8, 5])

        # [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]
        eta_arr = list(np.arange(0.7, 1.3, 0.05))
        val_arr = [1000, 2000, 3000, 4000]
        for val in val_arr:
            delta_arr = []
            for eta in eta_arr:
                # valu = val + delta
                # vall = val - delta
                # eta = valu / valn
                delta = val * (eta - 1) / (eta + 1)
                delta_arr.append(delta)

            delta_perc = np.array(delta_arr) / val * 100
            ax_arr[0].plot(eta_arr, delta_perc, color='red')
            ax_arr[0].scatter(eta_arr, delta_perc, color='red')

            ax_arr[1].plot(eta_arr, delta_arr, color='black')
            ax_arr[1].scatter(eta_arr, delta_arr, color='black')
            arg = '%s rpm' % val
            bbox_dict = dict(facecolor='white', edgecolor='none', alpha=0.8)
            ax_arr[1].text(eta_arr[-1]+0.01, delta_arr[-1], arg, bbox=bbox_dict)

            # # print to console
            # print('[eta_delta_equiv] eta_arr %s' % eta_arr)
            # print('[eta_delta_equiv] delta_arr %s' % delta_arr)
            # print('[eta_delta_equiv] delta_perc %s' % delta_perc)

        xlim = [eta_arr[0] - 0.1, eta_arr[-1] + 0.1]

        ax_arr[0].grid(True)
        ax_arr[0].set_xlim(xlim)
        # ax_arr[0].set_ylim([0, 15])
        ax_arr[0].axes.xaxis.set_ticklabels([])
        ax_arr[0].set(xlabel='', ylabel='$\Delta$ rotor speed, %')

        ax_arr[1].grid(True)
        ax_arr[1].set_xlim(xlim)
        # ax_arr[0].set_ylim([0, 15])
        # ax_arr[0].axes.xaxis.set_ticklabels([])
        ax_arr[1].set(xlabel='Rotor speed ratio $\eta$',
                      ylabel='$\Delta$ rotor speed')

        plt.savefig('/home/tzo4/Dropbox/tomas/pennState/avia/firefly_logBook/'
                    '2020-12-22_firefly_mixer/plots/' + 'eta_delta_equiv.jpg')


if __name__ == '__main__':
    u_testfile_arr = [
        'test1.pkl', 'test2.pkl', 'test3.pkl', 'test4.pkl', 'test5.pkl',
        'test6.pkl', 'test7.pkl', 'test8.pkl', 'test9.pkl', 'test10.pkl'
    ]

    u_motor1 = 4
    u_motor2 = 7
    u_mx_my = "m%s_m%s" % (u_motor1, u_motor2)
    u_filename = 'ars_dec22_summary_%s.jpg' % u_mx_my
    ArsDec22DataSummary.plot(u_motor1, u_motor2, u_testfile_arr, u_filename)

    u_motor1 = 3
    u_motor2 = 8
    u_mx_my = "m%s_m%s" % (u_motor1, u_motor2)
    u_filename = 'ars_dec22_summary_%s.jpg' % u_mx_my
    ArsDec22DataSummary.plot(u_motor1, u_motor2, u_testfile_arr, u_filename)

    # [plot] mx_my m4_m7
    # [plot] total current pol(0.9389598227492725) 9.806386751461247, pol(1) 9.884968421081556
    # [plot] total power saving 0.7949612611075116
    # [plot] del ta current pol(0.9587683354816365) 0.0, pol(1) 0.6913387924237675
    # [plot] mx_my m3_m8
    # [plot] total current pol(1.048917288994637) 10.335821625192285, pol(1) 10.3565844333112
    # [plot] total power saving 0.20047930138176856
    # [plot] delta current pol(1.0391986562318472) 0.0, pol(1) -0.7094759027900643

    # u_testfile_arr = ['test11.pkl', 'test12.pkl']
    #
    # u_motor1 = 4
    # u_motor2 = 7
    # u_mx_my = "m%s_m%s" % (u_motor1, u_motor2)
    # u_filename = 'ars_dec22_inflight_%s.jpg' % u_mx_my
    # ArsDec22DataSummary.plot(u_motor1, u_motor2, u_testfile_arr, u_filename)
    #
    # u_motor1 = 3
    # u_motor2 = 8
    # u_mx_my = "m%s_m%s" % (u_motor1, u_motor2)
    # u_filename = 'ars_dec22_inflight_%s.jpg' % u_mx_my
    # ArsDec22DataSummary.plot(u_motor1, u_motor2, u_testfile_arr, u_filename)

    ArsDec22DataSummary.eta_delta_equiv()

    # p1 = 9.33
    # p0 = 10.15
    # psav = (p1-p0)/p0*100
    # print('[plot] total power saving %s' % psav)
    # total power saving -8.07881773399015

    # Single Nb = 2
    # 319.16
    # 465.29
    # 628.71

    # Signle Nb = 3
    # 322.31
    # 469.88
    # 634.91

    # Single Nb = 6
    # 335.23
    # 488.72
    # 660.37

    # Coaxial Nb = 2 eta_thrust in [1, 2]
    # 300.42
    # 465.39
    # 605.32

    # Coaxial Nb = 2 eta_thrust in [2, 3]
    # 304.11
    # 473.70
    # 610.16

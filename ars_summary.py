#!/usr/bin/env python

from toopazo_tools.matplotlib import plt

from ars_dec22_data import ArsDec22Data

import numpy as np
import pickle
import copy
import matplotlib
matplotlib.rcParams.update({'font.size': 14})


class ArsSummary:
    # indx_arr = list(range(0, 22))
    name_arr = [
        'status_mean',  # 0
        'status_std',  # 0

        'outa_mean',  # 0
        'outa_std',  # 1
        'pwma_mean',  # 2
        'pwma_std',  # 3
        'rpma_mean',  # 4
        'rpma_std',  # 5
        'cura_mean',  # 6
        'cura_std',  # 7

        'outb_mean',  # 8
        'outb_std',  # 9
        'pwmb_mean',  # 10
        'pwmb_std',  # 11
        'rpmb_mean',  # 12
        'rpmb_std',  # 13
        'curb_mean',  # 14
        'curb_std',  # 15

        'twin',  # 16
        'dout_avg',  # 17
        'dpwm_avg',  # 18
        'drpm_avg',  # 19
        'dcur_avg',  # 20
        'tcur_avg',  # 21
    ]

    @staticmethod
    def indx_to_name(indx):
        name_arr = ArsSummary.name_arr
        # indx_arr = ArsDec22DataSummary.indx_arr
        # return name_arr[indx_arr.index(indx)]
        return name_arr[indx]

    @staticmethod
    def name_to_indx(name):
        name_arr = ArsSummary.name_arr
        # indx_arr = ArsDec22DataSummary.indx_arr
        # indx = indx_arr[name_arr.index(name)]
        return name_arr.index(name)

    @staticmethod
    def plot_summary(motor1, motor2, test_file_arr, filename):
        fig, ax_arr = plt.subplots(2, 1, figsize=[8, 6])

        mx_my = "m%s_m%s" % (motor1, motor2)
        print('[plot] mx_my %s' % mx_my)
        # fig.suptitle('Average hover performance: %s' % mx_my)
        # fig.suptitle('Coaxial rotor: Mean hover performance '
        #              'at different speed ratios $\eta_\Omega$')

        bbox_dict = dict(facecolor='white', edgecolor='none', alpha=0.8)

        dec22_dict = ArsSummary.load_pkl_files(test_file_arr)
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
        ax_arr[0].set(xlabel='', ylabel='Total current, A')
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
        [x_arr, p_arr, pol] = ArsSummary.polyfit(x_arr, y_arr, 2)
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
        psav = (pol(1) - pol(x0)) / pol(1) * 100
        print('[plot] total power saving %s' % psav)

        ax = ax_arr[0]
        arg = 'Minimum current at $\eta_{\Omega}$ %s' % round(x0, 2)
        ymin = 2
        ymax = 12
        ArsSummary.add_polyfit_to_subplot(
            ax, x_arr, p_arr, pol, arg, ymin, ymax)

        # polynomial fit to delta current
        if include_default:
            x_arr = np.hstack((default_eta_rpm, custom_eta_rpm))
            y_arr = np.hstack((default_dcur_avg, custom_dcur_avg))
        else:
            x_arr = custom_eta_rpm
            y_arr = custom_dcur_avg
        [x_arr, p_arr, pol] = ArsSummary.polyfit(x_arr, y_arr, 1)

        x0 = np.real(pol.roots[0])
        print('[plot] delta current pol(%s) %s, pol(1) %s'
              % (x0, pol(x0), pol(1)))

        ax = ax_arr[1]
        arg = 'Equal torque at $\eta_{\Omega}$ %s' % round(x0, 2)
        ymin = -5
        ymax = +5
        ArsSummary.add_polyfit_to_subplot(
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
            for name in ArsSummary.name_arr:
                indx = ArsSummary.name_to_indx(name)
                data = syndata_timebars[indx]
                testvalue[name] = data

            testdict[testkey] = testvalue
        return testdict

    @staticmethod
    def load_pkl_files(test_file_arr):
        # dec22dict= {'m3_m8_1': {'outa_mean': outa_mean_arr,
        # .. , 'tcur_avg': tcur_avg_arr}}
        emtpy_testdict = {}
        name_arr = ArsSummary.name_arr
        for indx in range(0, len(name_arr)):
            testkey = ArsSummary.indx_to_name(indx)
            testvalue = np.nan
            emtpy_testdict[testkey] = testvalue

        # testkey = m3_m8_1, m3_m8_2, m4_m7_1, m4_m7_2

        pkl_dict = {}
        for testfile in test_file_arr:
            fpath = ArsDec22Data.bdir + '/plots/' + testfile
            testdict = ArsSummary.pkl_parser(fpath)

            # Initialize vardict
            if not list(testdict.keys())[0] in pkl_dict:
                for testkey in testdict.keys():
                    pkl_dict[testkey] = copy.deepcopy(emtpy_testdict)

            # Append testdict to dec22dict
            for testkey, testvalue in testdict.items():
                for name, data in testvalue.items():
                    if pkl_dict[testkey][name] is np.nan:
                        pkl_dict[testkey][name] = np.array([data])
                    else:
                        pkl_dict[testkey][name] = \
                            np.hstack([pkl_dict[testkey][name], np.array(data)])

        # dec22dict = ArsDec22DataSummary.dict_info(dec22dict)
        return pkl_dict

    @staticmethod
    def polyfit(x_arr, y_arr, deg):
        # polynomial fit, p(x) = p[0] * x**deg + ... + p[deg]
        i_arr = np.argsort(x_arr)
        x_arr = x_arr[i_arr]
        y_arr = y_arr[i_arr]
        pol = np.poly1d(np.polyfit(x_arr, y_arr, deg=deg))
        # print(model)
        p_arr = []

        # Create x_arr with dynamic limits and including 1.0
        x_min = np.min(x_arr)
        x_max = np.max(x_arr)
        x_arr = np.linspace(x_min - 0.1, x_max + 0.1, 100)
        indx = np.argwhere(x_arr > 1.0)
        indx = indx.flatten()
        indx = indx[0]
        x_arr = np.insert(x_arr, indx, 1.0)

        for i in range(0, len(x_arr)):
            x = x_arr[i]
            p_arr.append(pol(x))

        return [x_arr, p_arr, pol]

    @staticmethod
    def add_polyfit_to_subplot(ax, x_arr, p_arr, pol, arg, ymin, ymax):
        ax.plot(x_arr, p_arr, color='black')
        # ax_arr[0].text(1, 5, str(pol.roots))
        x0 = round(np.real(pol.roots[0]), 2)
        ax.vlines(x=x0, ymin=ymin, ymax=ymax, colors='k', linestyles='dashed')
        # arg = 'Minimum current at $\eta_{\Omega}$ %s' % x0
        bbox_dict = dict(facecolor='white', edgecolor='none', alpha=0.8)
        ax.text(x0+0.05, ymin, arg, bbox=bbox_dict)


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

    # I am not including 'test11.pkl', 'test12.pkl' because it make the
    # polyfit-calculated minimum power go ouside data range (extrapoltation)
    u_testfile_arr = [
        'test1.pkl', 'test2.pkl', 'test3.pkl', 'test4.pkl', 'test5.pkl',
        'test6.pkl', 'test7.pkl', 'test8.pkl', 'test9.pkl', 'test10.pkl'
    ]

    u_motor1 = 4
    u_motor2 = 7
    u_mx_my = "m%s_m%s" % (u_motor1, u_motor2)
    u_filename = 'ars_dec22_summary_%s.jpg' % u_mx_my
    ArsSummary.plot_summary(u_motor1, u_motor2, u_testfile_arr, u_filename)

    u_motor1 = 3
    u_motor2 = 8
    u_mx_my = "m%s_m%s" % (u_motor1, u_motor2)
    u_filename = 'ars_dec22_summary_%s.jpg' % u_mx_my
    ArsSummary.plot_summary(u_motor1, u_motor2, u_testfile_arr, u_filename)

# [plot] mx_my m4_m7
# [plot] p_arr[np.argwhere(np.array(x_arr) == 1)] 10.028305588648912
# [plot] x_arr[np.argwhere(np.array(x_arr) == 1)] 1.0
# [plot] p_arr[np.argmin(np.array(p_arr))] 9.80110606417444
# [plot] x_arr[np.argmin(np.array(p_arr))] 0.896969696969697
# [plot] total current pol(0.8944144177213509) 9.800972917797957,
# pol(1) 10.028305588648912
# [plot] total power saving 2.266910086069522
# [plot] delta current pol(0.9457584949512742) 0.0, pol(1) 0.9317563163954468
# [plot] saving filename ars_dec22_summary_m4_m7.jpg
# [plot] mx_my m3_m8
# [plot] p_arr[np.argwhere(np.array(x_arr) == 1)] 10.57016097497458
# [plot] x_arr[np.argwhere(np.array(x_arr) == 1)] 1.0
# [plot] p_arr[np.argmin(np.array(p_arr))] 10.568228517219364
# [plot] x_arr[np.argmin(np.array(p_arr))] 1.018181818181818
# [plot] total current pol(1.016371368295297) 10.568204591943946, pol(1) 10.57016097497458
# [plot] total power saving 0.01850854528390299
# [plot] delta current pol(1.0310702706277246) 0.0, pol(1) -0.5809539023892256
# [plot] saving filename ars_dec22_summary_m3_m8.jpg

#!/usr/bin/python3

import sys
# import numpy as np
# import signal
# import time
# import datetime
from toopazo_tools.file_folder import FileFolderTools as FFTools
from toopazo_tools.telemetry import TelemetryLogger
# from kdecan_interface import KdeCanIface
from ars_interface import ArsIface


class ArsIfaceWrapper:
    def __init__(self):
        self.ars = ArsIface()
        self.esc_arr = list(range(11, 19))

    def get_data(self):
        log_data = self.ars.safely_read_data()
        print('[get_data] log_data {}'.format(log_data))
        return log_data

    def close(self):
        self.ars.serial_thread_close()


def parse_user_arg(folder):
    folder = FFTools.full_path(folder)
    print('target folder {}'.format(folder))
    if FFTools.is_folder(folder):
        cwd = FFTools.get_cwd()
        print('current folder {}'.format(cwd))
    else:
        arg = '{} is not a folder'.format(folder)
        raise RuntimeError(arg)
    return folder


if __name__ == '__main__':
    telem_folder = parse_user_arg(sys.argv[1])
    telem_iface = ArsIfaceWrapper()
    telem_ext = ".ars"
    telem_logger = TelemetryLogger(telem_folder, telem_iface, telem_ext)

    sampling_period = 0.1
    # data = {
    #     'header': {
    #         'sps': 200, 'mills': 9000, 'secs': 9.0, 'dtmills': 9000
    #     },
    #     'data': [0, 0, 0, 0, 0, 0, 0, 0, 510, 520, 507, 548, 10, 14,
    #              17, 19]
    # }
    fields = ["sps", "mills", "secs", "dtmills",
              "cur1", "cur2", "cur3", "cur4",
              "cur5", "cur6", "cur7", "cur8",
              "rpm1", "rpm2", "rpm3", "rpm4",
              "rpm5", "rpm6", "rpm7", "rpm8"]
    log_header = ", ".join(fields)
    telem_logger.live_data(sampling_period, log_header)


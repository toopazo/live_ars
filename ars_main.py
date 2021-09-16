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

    usampling_period = 0.1
    ulog_header = "time s, escid, "\
                  "voltage V, current A, angVel rpm, temp degC, warning, " \
                  "inthtl us, outthtl perc"
    telem_logger.live_data(usampling_period, ulog_header)


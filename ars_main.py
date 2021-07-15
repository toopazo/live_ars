#!/usr/bin/env python

# import time
import serial
import numpy as np
import pprint
# import io
import signal
import csv
import sys


class ArsWriter:
    def __init__(self, filename):
        self.ser = serial.Serial(
            port='/dev/ttyACM0',
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )
        self.pp = pprint.PrettyPrinter(indent=4, width=120, compact=True)
        self.log_fd = open(filename, 'w', encoding="utf-8")
        self.log_csv_writer = csv.writer(self.log_fd)
        # self.log_csv_writer.writerow(fields)
        self.pp.pprint(type(self.log_fd))
        self.sigint = False

    def run(self):
        while not self.sigint:
            x = self.ser.readline()
            # print(x)
            y = ArsWriter.parse_line(x)
            self.pp.pprint(y)
            self.write_to_file(y)
        self.log_fd.close()

    def sigint_handler(self, _signal, _frame):
        self.pp.pprint('[sigint] signal.SIGINT (ID: {}) has been caught'.format(_signal))
        self.sigint = True

    def write_to_file(self, xdict):
        # aassert isinstance(fd, io.FileIO)
        # fd.writelines([xdict])
        mkey = 'data'
        if mkey in xdict.keys():
            # datastr = self.pp.pformat(xdict[mkey])
            # datastr = str(xdict[mkey])
            # self.fd.write(datastr + '\r\n')
            self.log_csv_writer.writerow(xdict[mkey])
        else:
            pass

    @staticmethod
    def parse_line(line):
        # b'100,75000,75.000,1: 0,0,0,0,0,0,0,0,418,413,407,401,396,390,384,397,\r\n'
        # line = header:data
        # header = cnt, tms, tms/1000, mills()-tms
        # data = s0,s1,s2,s3,s4,s5,s6,s7,s8,s8,s10,s11,s12,s13,s14,s15

        # print(type(line))
        line = line.decode("utf-8")
        # print(type(line))
        assert isinstance(line, str)
        hd_sep = ':'
        cm_sep = ','
        if hd_sep not in line:
            return {'Error': '[parse_line] unrecognized format'}
        else:
            hd = line.split(hd_sep)
            # print(hd)
            header = hd[0]
            data = hd[1]
            h = header.split(cm_sep)
        if len(h) != 4:
            return {'Error': '[parse_line] header fields do not match'}
        else:
            header_dict = {'sps': int(h[0]), 'mills': int(h[1]),
                           'secs': float(h[2]), 'dtmills': int(h[3])}
        data = data.split(cm_sep)
        data.pop()  # get rid of '\r\n'
        data = np.array(data, np.int)
        return {'header': header_dict, 'data': data}


if __name__ == '__main__':
    ardusensor = ArsWriter(sys.argv[1])
    signal.signal(signal.SIGINT, ardusensor.sigint_handler)
    ardusensor.run()

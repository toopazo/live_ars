#!/usr/bin/env python

# import time
import serial
import numpy as np
import pprint
# import io
# import signal
# import csv
# import sys
import threading


class ArsIface:
    def __init__(self, port):
        self.serial = serial.Serial(
            port=port,
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )

        self.serial_data = ""
        self.serial_thread_lock = threading.Lock()
        self.serial_thread_event = threading.Event()
        self.serial_thread = threading.Thread(
            target=self.serial_thread_main, args=(self.serial_thread_event,))
        self.serial_thread.start()
        # self.thread1.join()

    def serial_thread_main(self, close_event):
        assert isinstance(close_event, threading.Event)
        while not close_event.is_set():
            line = self.serial.readline()
            data = ArsIface.parse_line(line)
            # data = {
            #     'header': {
            #         'sps': 200, 'mills': 9000, 'secs': 9.0, 'dtmills': 9000
            #     },
            #     'data': [0, 0, 0, 0, 0, 0, 0, 0, 510, 520, 507, 548, 10, 14,
            #              17, 19]
            # }

            # print('[serial_thread_main] data {}'.format(data))
            if 'error' in data.keys():
                print('[serial_thread_main] Error {}'.format(data['error']))
                continue
            data_arr = [
                data['header']['sps'], data['header']['mills'],
                data['header']['secs'], data['header']['dtmills'],
            ]
            # data_arr = data_arr.append(data['data'])
            data_arr = data_arr + list(data['data'])
            data = ', '.join(map(str, data_arr))
            self.safely_write_data(data)
        self.serial.close()

    def serial_thread_close(self):
        self.serial_thread_event.set()
        # blocks the calling thread until the thread whose join() method is
        # called is terminated.
        self.serial_thread.join()

    def safely_read_data(self):
        if self.serial_thread_lock.locked():
            print('[safely_read_data] lock is taken, we need to wait ..')
        self.serial_thread_lock.acquire()
        var = self.serial_data
        self.serial_thread_lock.release()
        return var

    def safely_write_data(self, data):
        if self.serial_thread_lock.locked():
            print('[safely_write_data] lock is taken, we need to wait ..')
        self.serial_thread_lock.acquire()
        self.serial_data = data
        self.serial_thread_lock.release()

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
            return {'error': '[parse_line] unrecognized format'}
        else:
            hd = line.split(hd_sep)
            # print(hd)
            header = hd[0]
            data = hd[1]
            h = header.split(cm_sep)
        if len(h) != 4:
            return {'error': '[parse_line] header fields do not match'}
        else:
            header_dict = {'sps': int(h[0]), 'mills': int(h[1]),
                           'secs': float(h[2]), 'dtmills': int(h[3])}
        data = data.split(cm_sep)
        data.pop()  # get rid of '\r\n'
        data = np.array(data, np.int)
        return {'header': header_dict, 'data': data}

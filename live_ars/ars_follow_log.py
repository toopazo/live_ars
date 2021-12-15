import time
import os
import sys


def follow(fd):
    """
    Generator function that yields new lines in a file
    :param fd:
    :return:
    """
    # seek the end of the file
    fd.seek(0, os.SEEK_END)

    # start infinite loop
    while True:
        # read last line of file
        line = fd.readline()  # sleep if file hasn't been updated
        if not line:
            time.sleep(0.1)
            continue
        yield line


if __name__ == '__main__':
    u_filename = sys.argv[1]
    print(f'reading {u_filename} ..')
    u_logfd = open(u_filename)
    u_loglines = follow(u_logfd)
    # iterate over the generator
    for u_line in u_loglines:
        print(u_line)
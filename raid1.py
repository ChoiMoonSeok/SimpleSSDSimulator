import sys

import FTL
import MS_FTL
import VARIABLE

path = sys.argv[1]


def main(path):
    io_count = 0
    total_latency = 0

    disk0 = FTL.FTL(VARIABLE.SSD_CAPACITY,
                    VARIABLE.PAGE_PER_BLOCK, VARIABLE.PAGE_CAPACITY, VARIABLE.GC_THRESHOLD)
    disk1 = FTL.FTL(VARIABLE.SSD_CAPACITY,
                    VARIABLE.PAGE_PER_BLOCK, VARIABLE.PAGE_CAPACITY, VARIABLE.GC_THRESHOLD)

    with open(path) as f:
        lines = f.readlines()

        for line in lines[1:]:
            lba, size, dt = map(int, line.strip().split(sep=',')[1:])

            io_count += 1
            total_latency += max(disk0.write(lba, size),
                                 disk1.write(lba, size))

    print('**************************')
    print('Normal SSD')
    print(f'io_count : {io_count}')
    print(f'Disk0 GC count : {disk0.GC_COUNT}')
    print(f'Disk1 GC count : {disk1.GC_COUNT}')
    print(f'Disk0 WAF : {disk0.TOTAL_WRITE_COUNT / disk0.USER_WRITE_COUNT}')
    print(f'Disk1 WAF : {disk1.TOTAL_WRITE_COUNT / disk1.USER_WRITE_COUNT}')
    print(f'Avg Latency : {total_latency / io_count}ms')
    print('**************************')
    print()

    io_count = 0
    total_latency = 0

    disk0 = MS_FTL.MS_FTL(VARIABLE.SSD_CAPACITY,
                          VARIABLE.PAGE_PER_BLOCK, VARIABLE.PAGE_CAPACITY, VARIABLE.GC_THRESHOLD)
    disk1 = MS_FTL.MS_FTL(VARIABLE.SSD_CAPACITY,
                          VARIABLE.PAGE_PER_BLOCK, VARIABLE.PAGE_CAPACITY, VARIABLE.GC_THRESHOLD)

    with open(path) as f:
        lines = f.readlines()

        for line in lines[1:]:
            lba, size, dt = map(int, line.strip().split(sep=',')[1:])

            io_count += 1
            total_latency += max(disk0.write(lba, size, dt),
                                 disk1.write(lba, size, dt))

    print('**************************')
    print('Multi Streamed SSD')
    print(f'io_count : {io_count}')
    print(f'Disk0 GC count : {disk0.GC_COUNT}')
    print(f'Disk1 GC count : {disk1.GC_COUNT}')
    print(f'Disk0 WAF : {disk0.TOTAL_WRITE_COUNT / disk0.USER_WRITE_COUNT}')
    print(f'Disk1 WAF : {disk1.TOTAL_WRITE_COUNT / disk1.USER_WRITE_COUNT}')
    print(f'Avg Latency : {total_latency / io_count}ms')
    print('**************************')
    print()


if __name__ == "__main__":
    main(path)

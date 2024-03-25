import sys
from tqdm import tqdm

import FTL
import MS_FTL
import VARIABLE

path = sys.argv[1]


def main(trace_path):
    io_count = 0
    total_latency = 0
    io_count_ms = 0
    total_latency_ms = 0

    ssd = FTL.FTL(VARIABLE.SSD_CAPACITY, VARIABLE.PAGE_PER_BLOCK,
                  VARIABLE.PAGE_CAPACITY, VARIABLE.GC_THRESHOLD, VARIABLE.GC_POLICY)

    with open(trace_path) as f:
        lines = f.readlines()

        for line in tqdm(lines[1:]):
            lba, size, dt = map(int, line.strip().split(sep=',')[1:])

            io_count += 1
            total_latency += ssd.write(lba, size)

    print('**************************')
    print('Normal SSD')
    print(f'io_count : {io_count}')
    print(f'GC count : {ssd.GC_COUNT}')
    print(f'WAF : {ssd.TOTAL_WRITE_COUNT / ssd.USER_WRITE_COUNT}')
    print(f'Avg Latency : {total_latency / io_count}ms')
    print('**************************')
    print()


if __name__ == "__main__":
    main(path)

import math
from collections import deque

import SSD_CLASS
import VARIABLE


class MS_FTL:

    GC_COUNT = 0
    USER_WRITE_COUNT = 0
    TOTAL_WRITE_COUNT = 0

    def __init__(self, ssd_capa, page_per_block, page_size, gc_threshold):
        self.CAPACITY = ssd_capa
        self.PAGE_PER_BLOCK = page_per_block
        self.PAGE_SIZE = page_size
        self.GC_threshold = gc_threshold

        print('init multi streamed ssd')

        # block & page 생성
        self.blocks = [SSD_CLASS.block(VARIABLE.TLC, [SSD_CLASS.page() for _ in range(self.PAGE_PER_BLOCK)], i)
                       for i in range(self.CAPACITY * 1024 * 1024 // (self.PAGE_PER_BLOCK * self.PAGE_SIZE))]

        self.free_blocks = deque([i for i in range(len(self.blocks))])

        self.lpn_pool = deque(i for i in range(
            self.CAPACITY * 1024 * 1024 // self.PAGE_SIZE))

        print('create block & page')

        # 맵핑 테이블
        self.lba_lpn = dict()
        self.lpn_ppn = dict()
        self.ppn_lpn = dict()

        self.write_ptr0 = self.free_blocks.pop()
        self.write_ptr1 = self.free_blocks.pop()
        self.write_ptr2 = self.free_blocks.pop()
        self.write_ptr3 = self.free_blocks.pop()
        self.write_ptr4 = self.free_blocks.pop()
        self.write_ptr5 = self.free_blocks.pop()

    def get_block_id_from_ppn(self, ppn):
        return ppn // self.PAGE_PER_BLOCK

    def get_page_index(self, ppn):
        return ppn % self.PAGE_PER_BLOCK

    def write(self, lba, size, s_id):
        total_latency = 0

        wp = eval(f'self.write_ptr{s_id}')

        while len(self.free_blocks) < self.CAPACITY * 1024 * (1 - self.GC_threshold):
            self.gc(s_id)
            self.GC_COUNT += 1
            total_latency += VARIABLE.ERASE_LATENCY

        page_num = math.ceil(size / 1024)

        self.USER_WRITE_COUNT += page_num
        self.TOTAL_WRITE_COUNT += page_num

        # 기존에 저장되어 있던 page 삭제
        if self.lba_lpn.get(lba) != None:

            old_lpns = self.lba_lpn.get(lba)

            for lpn in old_lpns:
                self.lpn_pool.appendleft(lpn)

                block_id = self.get_block_id_from_ppn(self.lpn_ppn[lpn])
                page_idx = self.get_page_index(self.lpn_ppn[lpn])

                self.blocks[block_id].pages[page_idx].valid = False
                self.blocks[block_id].invalid_count += 1

        self.lba_lpn[lba] = [self.lpn_pool.pop() for _ in range(page_num)]

        for lpn in self.lba_lpn[lba]:
            total_latency += VARIABLE.WRITE_LATENCY

            if self.blocks[wp].block_write_ptr < VARIABLE.PAGE_PER_BLOCK - 1:
                self.lpn_ppn[lpn] = self.blocks[wp].write_page()
                self.ppn_lpn[self.lpn_ppn[lpn]] = lpn
            else:
                if s_id == 0:
                    self.write_ptr0 = self.free_blocks.pop()
                elif s_id == 1:
                    self.write_ptr1 = self.free_blocks.pop()
                elif s_id == 2:
                    self.write_ptr2 = self.free_blocks.pop()
                elif s_id == 3:
                    self.write_ptr3 = self.free_blocks.pop()
                elif s_id == 4:
                    self.write_ptr4 = self.free_blocks.pop()
                elif s_id == 5:
                    self.write_ptr5 = self.free_blocks.pop()

                wp = eval(f'self.write_ptr{s_id}')
                self.lpn_ppn[lpn] = self.blocks[wp].write_page()
                self.ppn_lpn[self.lpn_ppn[lpn]] = lpn

        return total_latency

    def gc(self, s_id):

        wp = eval(f'self.write_ptr{s_id}')

        max_invalid = 0
        gc_block = None
        for idx, block in enumerate(self.blocks):
            if block.blk_id != wp:
                if block.invalid_count > max_invalid:
                    gc_block = idx
                    max_invalid = block.invalid_count

        valid_ppns = self.blocks[gc_block].erase_block()
        self.free_blocks.appendleft(gc_block)

        for old_ppn in valid_ppns:

            self.TOTAL_WRITE_COUNT += 1

            lpn = self.ppn_lpn[old_ppn]

            if self.blocks[wp].block_write_ptr < VARIABLE.PAGE_PER_BLOCK - 1:
                self.lpn_ppn[lpn] = self.blocks[wp].write_page()
                self.ppn_lpn[self.lpn_ppn[lpn]] = lpn
            else:
                if s_id == 0:
                    self.write_ptr0 = self.free_blocks.pop()
                elif s_id == 1:
                    self.write_ptr1 = self.free_blocks.pop()
                elif s_id == 2:
                    self.write_ptr2 = self.free_blocks.pop()
                elif s_id == 3:
                    self.write_ptr3 = self.free_blocks.pop()
                elif s_id == 4:
                    self.write_ptr4 = self.free_blocks.pop()
                elif s_id == 5:
                    self.write_ptr5 = self.free_blocks.pop()

                wp = eval(f'self.write_ptr{s_id}')
                self.lpn_ppn[lpn] = self.blocks[wp].write_page()
                self.ppn_lpn[self.lpn_ppn[lpn]] = lpn

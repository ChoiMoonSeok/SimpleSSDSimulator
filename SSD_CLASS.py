import VARIABLE


class page:
    def __init__(self):
        self.valid = False


class block:
    def __init__(self, erase_limit, pages, blk_num):
        self.ERASE_LIMIT = erase_limit
        self.invalid_count = 0
        self.pages = pages
        self.blk_id = blk_num
        self.block_write_ptr = 0

    def erase_block(self):
        self.ERASE_LIMIT -= 1
        self.idx = 0
        self.invalid_count = 0

        valid_pages = []
        for idx, page in enumerate(self.pages):
            if page.valid == True:
                valid_pages.append(self.blk_id * VARIABLE.PAGE_PER_BLOCK + idx)
            page.valid = False

        return valid_pages

    def write_page(self):
        self.pages[self.block_write_ptr].valid = True

        self.block_write_ptr += 1

        return self.blk_id * VARIABLE.PAGE_PER_BLOCK + self.block_write_ptr - 1

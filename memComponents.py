
import binascii


class Virtual_Address:
    def __init__(self, address, page, offset):
        self.address = address
        self.page_num   = page
        self.offset  = offset

    def __str__(self):
        return f"Page {self.page_num:03}\tOffset {self.offset:03}"

class TLB_ENTRY:
    def __init__(self, page, frame):
        self.page_num   = page
        self.frame_num  = frame
    def __str__(self):
        return str(f"{self.page_num:03} {self.frame_num:03}")

class TLB:
    def __init__(self, size):
        self.size = size
        self.entries = []
        for i in range(0,size):
            self.entries.append(TLB_ENTRY(-1,0))

    def lookup(self, target_page_num, pagetable):
        for i in range(0, self.size):
            if(self.entries[i].page_num == target_page_num):
                pagetable.entries[target_page_num].access_time = pagetable.timer
                return self.entries[i].frame_num
        return -1

    def add(self, page_num, frame_num):
        self.entries.pop(0)
        self.entries.append(TLB_ENTRY(page_num,frame_num))


    def remove(self, page_num):
        for i in range(0, self.size):
            if (self.entries[i].page_num == page_num):
                self.entries.pop(i)
                self.entries.append(TLB_ENTRY(-1, 0))
                return
        #print(f"{page_num} error")


class PT_ENTRY:
    def __init__(self, frame, val, wt, at):
        self.frame_num  = frame
        self.valid      = val
        self.write_time = wt
        self.access_time = at


class PAGE_TABLE:
    def __init__(self, size, frames, eviction_scheme, tlb, sequence):
        self.size = size
        self.frames = frames
        self.frames_used = 0
        self.entries = []
        self.timer = 0
        self.eviction_scheme = eviction_scheme
        self.tlb = tlb
        self.sequence = sequence

        for i in range(0,size):
            self.entries.append(PT_ENTRY(-1, 0, -1, -1))


    def incriment(self):
        self.timer = self.timer + 1
    def lookup(self, target_page_number):
        if self.entries[target_page_number].valid == 0:
            return -1
        self.entries[target_page_number].access_time = self.timer
        return self.entries[target_page_number].frame_num


    def add(self, page_num, tlb, ram, address, backing_store, ram_info):
        frame_num = self.frames_used
        if(self.frames_used >= self.frames):
            frame_num = self.evict(ram_info)
            #print(f"evicting: {frame_num}")
            #tlb.remove(page_num)
        self.entries[page_num].frame_num = frame_num
        self.entries[page_num].valid = 1
        self.entries[page_num].write_time = self.timer
        self.entries[page_num].access_time = self.timer
        self.frames_used = self.frames_used + 1
        ram.entries[frame_num] = backing_store.data[page_num]
        return frame_num

    def get_FIFO(self):
        first_time = -1
        index = 0
        for i in range(self.size):
            if(self.entries[i].valid):
                if((first_time < 0) or (self.entries[i].write_time < first_time)):
                    index = i
                    first_time = self.entries[i].write_time
        return index

    def get_LRU(self):
        first_time = -1
        index = 0
        for i in range(self.size):
            if (self.entries[i].valid):
                if ((first_time < 0) or (self.entries[i].access_time < first_time)):
                    index = i
                    first_time = self.entries[i].access_time
        return index
    def get_OPT(self,ram_info):
        access_time = [1000] * len(ram_info)
        sequence_remaining = self.sequence[self.timer:]
        for i in range(len(ram_info)):
            for j in range(len(sequence_remaining)):
                if(sequence_remaining[j].page_num == ram_info[i]):
                    if(j < access_time[i]):
                        access_time[i] = j

        value = max(access_time)
        index = access_time.index(value)
        return ram_info[index]


    def evict(self, ram_info):

        self.frames_used = self.frames_used - 1
        if(self.eviction_scheme == 'fifo'):
            index_to_evict = self.get_FIFO()
        elif(self.eviction_scheme == 'lru'):
            index_to_evict = self.get_LRU()
        elif (self.eviction_scheme == 'opt'):
            index_to_evict = self.get_OPT(ram_info)
        else:
            index_to_evict = self.get_FIFO()
        self.entries[index_to_evict].valid = 0
        self.tlb.remove(index_to_evict)
        return self.entries[index_to_evict].frame_num


class RAM:
    def __init__(self,frames):
        self.frames = frames
        self.entries = [None] * frames

class BACKING_STORE:
    def __init__(self):
        frame_size = 256
        num_entries = 256
        self.data = [None] * num_entries
        file_name = "BACKING_STORE.bin"
        with open(file_name, "rb") as file:
            for i in range(num_entries):
                self.data[i] = file.read(256)





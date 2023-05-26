#!/usr/local/bin python
import struct

from memComponents import *

def load(filename):
    sequence = []
    with open(filename, 'r') as file:
        for line in file:
            address = int(line.strip())
            page_num = (address>>8) & 0xFF
            offset = address & 0xFF
            sequence.append(Virtual_Address(address, page_num, offset))
    return sequence

if __name__ == '__main__':
    file_path = 'test1in.txt'  # Replace with the actual path to your file
    sequence = load(file_path)

    frames = 10
    tlb_hits = 0
    tlb_misses = 0
    num_faults = 0
    tlb = TLB(16)
    pageTable = PAGE_TABLE(256,frames,'fifo',tlb)
    ram = RAM(frames)
    backStore = BACKING_STORE()

    for address in sequence:
        frame_num = tlb.lookup(address.page_num)
        if(frame_num < 0):
            #print(f"TLB_MISS {address.page_num:03}")
            tlb_misses = tlb_misses + 1
            frame_num = pageTable.lookup(address.page_num)
            if(frame_num < 0):
                #print(f"Fault {address.page_num:03}")
                #print(address.address)
                num_faults = num_faults + 1
                frame_num = pageTable.add(address.page_num, ram, address, backStore)
            # else:
            #     print(f"SM {address.page_num:03}")
            tlb.add(address.page_num, 1)
        else:
            tlb_hits = tlb_hits + 1

        signed_int = ram.entries[frame_num][address.offset]
        if(signed_int > 127):
            signed_int = signed_int - 256
        print(f"{address.address}, {signed_int}, {frame_num}, {binascii.hexlify(ram.entries[frame_num]).decode('utf-8')}")

    print(f"Number of Translated Addresses = {len(sequence)}")
    print(f"Page Faults = {num_faults}")
    print(f"Page Fault Rate = {num_faults/len(sequence):.3f}")
    print(f"TLB Hits = {tlb_hits}")
    print(f"TLB Misses = {tlb_misses}")
    print(f"Page Fault Rate = {tlb_hits/(tlb_misses+tlb_hits):.3f}")
        # else:
            #print(f"TLB_H {address.page_num:03}")
        #print("")


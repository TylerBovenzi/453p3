#!/usr/bin/env python
import argparse
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

    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="the filename")
    parser.add_argument("frame_size", type=int, help="the frame size")
    parser.add_argument("option", choices=["OPT", "LRU", "FIFO"], help="the option (OPT, LRU, or FIFO)")

    args = parser.parse_args()
    file_path = args.filename
    sequence = load(file_path)

    frames = max(args.frame_size,1)

    tlb_hits = 0
    tlb_misses = 0
    num_faults = 0
    tlb = TLB(16)
    pageTable = PAGE_TABLE(256,frames,args.option,tlb,sequence)
    ram = RAM(frames)
    backStore = BACKING_STORE()

    ram_info = [None] * frames

    for address in sequence:
        pageTable.incriment()
        frame_num = tlb.lookup(address.page_num,pageTable)

        #frame_num = -1
        if(frame_num < 0):
            #print(f"TLB_MISS {address.page_num:03}")
            tlb_misses = tlb_misses + 1
            frame_num = pageTable.lookup(address.page_num)

            if(frame_num < 0):
                #print(f"Fault {address.page_num:03}")
                #print(address.address)
                num_faults = num_faults + 1
                frame_num = pageTable.add(address.page_num,tlb, ram, address, backStore, ram_info)
            #else:
            #     print(f"SM {address.page_num:03}")
            tlb.add(address.page_num, frame_num)
        else:
            #print(f"{address.address}, {frame_num}")
            tlb_hits = tlb_hits + 1

        signed_int = ram.entries[frame_num][address.offset]
        if(signed_int > 127):
            signed_int = signed_int - 256
        print(f"{address.address}, {signed_int}, {frame_num}, {binascii.hexlify(ram.entries[frame_num]).decode('utf-8')}")
        ram_info[frame_num] = address.page_num

    print(f"Number of Translated Addresses = {len(sequence)}")
    print(f"Page Faults = {num_faults}")
    print(f"Page Fault Rate = {num_faults/len(sequence):.3f}")
    print(f"TLB Hits = {tlb_hits}")
    print(f"TLB Misses = {tlb_misses}")
    print(f"Page Fault Rate = {tlb_hits/(tlb_misses+tlb_hits):.3f}")
        # else:
            #print(f"TLB_H {address.page_num:03}")
        #print("")


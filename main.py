from memComponents import *

def load(filename):
    sequence = []
    with open(filename, 'r') as file:
        for line in file:
            address = int(line.strip())
            page_num = (address>>8) & 0xFF
            offset = address & 0xFF
            sequence.append(Virtual_Address(page_num, offset))
    return sequence

if __name__ == '__main__':
    file_path = 'fifo5.txt'  # Replace with the actual path to your file
    sequence = load(file_path)

    tlb = TLB(5)
    pageTable = PAGE_TABLE(256,8,'fifo',tlb)

    for address in sequence:
        frame_num = tlb.lookup(address.page_num)
        if(frame_num < 0):
            print(f"TLB_MISS {address.page_num:03}")
            frame_num = pageTable.lookup(address.page_num)
            if(frame_num < 0):
                print(f"Fault {address.page_num:03}")
                pageTable.add(address.page_num)
            else:
                print(f"SM {address.page_num:03}")
            tlb.add(address.page_num, 1)
        else:
            print(f"TLB_H {address.page_num:03}")
        print("")
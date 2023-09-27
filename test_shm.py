# -*- coding: utf-8 -*-
from multiprocessing import shared_memory
import multiprocessing
import time
import struct
import os
'''
0                   1                   2                   3
  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |V=0|                        length                             |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |                         Process Block                         |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |                         Process Block                         |
 |                             ...                               |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
'''
class TaskControl:
    def __init__(self, name=None):
        self._version = 0
        self._process_count = 0
        self._name = name
        # 预分配1页, 可以支持341个进程管理
        if name is None:
            self._shm = shared_memory.SharedMemory(create=True, size=4096)
        else:
            self._shm = shared_memory.SharedMemory(name, size=4096)
        # uint8_t ==> version, uint8_t ==> process count
        self._header_format = "BB"
        # uint32_t ==> pid, uint32_t ==> status, uint32_t ==> flag
        self._process_block_format = "III"
        self._header_size = struct.calcsize(self._header_format)
        self._process_block_size = struct.calcsize(self._process_block_format)

    def init(self, version = 0, process_count = 0):
        if self._name is None:
            self._version = version
            self._process_count = process_count
            self.__write(0, self._header_format, version, process_count)
        else:
            self._version, self._process_count = self.__read(self._header_format, 0)
        return self._shm.name

    def get_process_info(self, index):
        if index >= self._process_count:
            print(f"index {index} exceed process count {self._process_count}")
            return None
        return self.__read(self._process_block_format, self._header_size + index * self._process_block_size)

    def save_process_info(self, index, *args):
        print(f"save process info {index} --> {args}")
        if index >= self._process_count:
            print(f"index {index} exceed process count {self._process_count}")
            return None
        if len(args) < 3:
            print(f"archive process info {args} invalid")
            return None
        return self.__write(self._header_size + index * self._process_block_size, self._process_block_format, *args)

    def __read(self, format, position):
        return struct.unpack(format, self._shm.buf[position:position + struct.calcsize(format)])

    def __write(self, position, format, *args):
        self._shm.buf[position:position + struct.calcsize(format)] = struct.pack(format, *args)

def process_is_alive(pid):
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True

def print_pid(name, index):
    control = TaskControl(name)
    control.init()
    control.save_process_info(index, multiprocessing.current_process().pid, 0, 0)
    while True:
        print(f"index:{index}, name: {name}, PID: {multiprocessing.current_process().pid}")
        time.sleep(1)

def start_child_processes(name):
    processes = []
    control = TaskControl(name)
    control.init()
    control.save_process_info(0, multiprocessing.current_process().pid, 0, 0)
    for i in range(4):
        p = multiprocessing.Process(target=print_pid, args=(name, i + 1))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

if __name__ == '__main__':
    control = TaskControl()
    name = control.init(0, 5)
    print(name)
    parent_process = multiprocessing.Process(target=start_child_processes, args=(name,))
    parent_process.start()
    time.sleep(10)
    while True:
        for i in range(5):
            pid , _, _ = control.get_process_info(i)
            print(f"process:{pid} is alived? {process_is_alive(pid)}")
        time.sleep(1)
    parent_process.join()
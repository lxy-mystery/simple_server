from acceptor import Acceptor
from worker import Worker

class MyWorker(Worker):
    def __init__(self, name, message_bus):
        super().__init__(name, message_bus)
    def on_request(self, request_data):
        return (self._name + request_data.decode("utf-8")).encode("utf-8")

    def on_close(self, fd):
        print("")
        return super().on_close(fd)


# 主进程负责管理acceptor进程
class Manager:
    def __init__(self):
        self._server = Acceptor(4, ("0.0.0.0", 9437), MyWorker)
    def run(self):
        self._server.start()

manager = Manager()
manager.run()

shm_a = shared_memory.SharedMemory(create=True, size=10)
type(shm_a.buf)

buffer = shm_a.buf
len(buffer)

buffer[:4] = bytearray([22, 33, 44, 55])  # Modify multiple at once
buffer[4] = 100                           # Modify single byte at a time
# Attach to an existing shared memory block
shm_b = shared_memory.SharedMemory(shm_a.name)
import array
array.array('b', shm_b.buf[:5])  # Copy the data into a new array.array

shm_b.buf[:5] = b'howdy'  # Modify via shm_b using bytes
bytes(shm_a.buf[:5])      # Access via shm_a

shm_b.close()   # Close each SharedMemory instance
shm_a.close()
shm_a.unlink()  # Call unlink only once to release the shared memory
'''
TaskControl
    command: start, stop, status
    main control block
        acceptor status
    acceptor control block
        pid
        worker control block
            worker id
            worker status
            pid

'''
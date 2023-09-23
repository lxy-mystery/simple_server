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

class Monitor:
    def __init__(self):
        pass

# 主进程负责管理acceptor进程
class Manager:
    def __init__(self):
        self._server = Acceptor(4, ("0.0.0.0", 9437), MyWorker)
    def run(self):
        self._server.start()

manager = Manager()
manager.run()
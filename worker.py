import socket
from multiprocessing import Process
import select
from eventloop import EventLoop

# worker进程负责处理新连接
class Worker(Process):
    def __init__(self, name, message_bus):
        print("create worker {}".format(name))
        super().__init__()
        self._name = name
        self._message_bus = message_bus
        self.loop = EventLoop("loop:" + self.name)
        self._sessions = {}
    def on_request(self, request_data):
        return request_data

    def on_close(self, fd):
        self.loop.unregister(fd)
        self._sessions[fd].close()

    def do_request(self, fd):
        request = self._sessions[fd].recv(4096)
        print("request data {}".format(request))
        if len(request) == 0:
            self.on_close(fd)
            return

        response = self.on_request(request)
        if response is not None:
            self.do_response(fd, response)

    def do_response(self, fd, response):
        self._sessions[fd].send(response)

    def on_recive_new_connection(self, message_bus):
        print(f"{self._name} get new connection...")
        message, fds, flags, addr  = socket.recv_fds(self._message_bus, 2048, 128)
        print("recv new [{}] connection".format(len(fds)))
        for fd in fds:
            self._sessions[fd] = socket.socket(socket.AF_INET, socket.SOCK_STREAM, fileno=fd)
            self.loop.register(fd, select.EPOLLIN, self.do_request)
            self.loop.register(self._message_bus.fileno(), select.EPOLLHUP, self.on_close)
            self.loop.register(self._message_bus.fileno(), select.EPOLLRDHUP, self.on_close)

    def on_error(self):
        exit(-1)

    def run(self):
        print("start worker {}".format(self._name))
        self.loop.register(self._message_bus.fileno(), select.EPOLLIN, self.on_recive_new_connection)
        self.loop.register(self._message_bus.fileno(), select.EPOLLHUP, self.on_error)
        self.loop.register(self._message_bus.fileno(), select.EPOLLRDHUP, self.on_error)
        # 启动事件循环
        self.loop.run()
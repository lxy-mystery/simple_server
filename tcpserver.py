
import socket
from multiprocessing import Process
import select

class EventLoop:
    def __init__(self):
        self._epoll_fd = select.epoll()
        self._fd_to_callback = {}

    def run(self):
        while True:
            events = self._epoll_fd.poll(20)
            for fd, event in events:
                if fd in self._fd_to_callback:
                    self._fd_to_callback[fd](fd, event)
                else:
                    print("not found this file description{} event {}".format(fd, event))
    def register(self, fd, callback):
        self._epoll_fd.register(fd, select.EPOLLIN | select.EPOLLOUT)
        self._fd_to_callback[fd] = callback

    def unregister(self, fd):
        self._epoll_fd.unregister(fd)
        del self._fd_to_callback[fd]

# worker进程负责处理新连接
class Worker:
    def __init__(self, name, message_bus):
        self._name = name
        self._message_bus = message_bus
        self.loop = EventLoop()

    def run(self):
        # 启动事件循环
        self.loop.run()

# Acceptor进程管理其他的Worker进程
class Acceptor:
    def __init__(self, worker_number, listen_address):
        self.loop = EventLoop()
        self._worker_number = worker_number
        self._workers = []
        self.message_bus = []
        self._listen_address = listen_address

    def _start_worker(self, index):
        pipe = socket.socketpair()
        self._workers.append(Worker("worker{}",format(index), pipe[1].fileno()))
        self.message_bus.append(pipe[0])

    def _start_server(self):
        pass

    def run(self):
        # 按照配置启动worker子进程
        for i in range(self.worker_number):
            self._start_worker(i)

        # 启动服务器
        self._start_server()

        # 启动acceptor的事件循环
        self.loop.run()

# 主进程负责管理acceptor进程
class Manager:
    def __init__(self):
        pass

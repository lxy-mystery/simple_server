from eventloop import EventLoop
from worker import Worker
from multiprocessing import Process
import socket
import select

# Acceptor进程管理其他的Worker进程
class Acceptor(Process):
    def __init__(self, worker_number, listen_address, worker_class=Worker):
        super().__init__()
        self.loop = EventLoop("acceptor")
        self._worker_class = worker_class
        self._worker_number = worker_number
        self._workers = []
        self.message_bus = []
        self._listen_address = listen_address
        self._current_worker_id = 0;
        self.listener = None

    def _start_worker(self, index):
        pipe = socket.socketpair()
        if len(self._workers) <= index:
            self._workers.append(self._worker_class("worker{}".format(index), pipe[1]))
            
        else:
            self._workers[index] = self._worker_class("worker{}".format(index), pipe[1])
        self._workers[index].start()

        if len(self.message_bus) <= index:
            self.message_bus.append(pipe[0])
        else:
            self.message_bus[index] = pipe[0]

    def on_idel(self):
        for index, worker in enumerate(self._workers):
            # print(f"id: {index} worker:{worker._name}, is alive:{worker.is_alive()}")
            if not worker.is_alive():
                print(f"id: {index} worker:{worker._name}, stoped. restart it now")
                self._start_worker(index)

    def _start_server(self):
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.setblocking(False)
        self.listener.bind(self._listen_address)
        self.listener.listen()
        print("register listener fd {}, event {}".format(self.listener.fileno(), select.EPOLLIN))
        self.loop.register(self.listener.fileno(), select.EPOLLIN, self.dispatch)
        self.loop.set_idel(self.on_idel)

    def _dispatch_rule(self):
        current_worker = self._current_worker_id
        self._current_worker_id = (self._current_worker_id + 1) % self._worker_number
        return current_worker

    def dispatch(self, socket_fd):
        worer_id = self._dispatch_rule()
        session_fd, address = self.listener.accept()
        print("dispatch fd:{} address {} to worker:{}, msgbug:{}".format(session_fd.fileno(), address, worer_id, self.message_bus[worer_id]))
        socket.send_fds(self.message_bus[worer_id],[b"Acceptor new Connection"], [session_fd.fileno()])

    def run(self):
        # 按照配置启动worker子进程
        for i in range(self._worker_number):
            self._start_worker(i)

        # 启动服务器
        self._start_server()

        # 启动acceptor的事件循环
        self.loop.run()
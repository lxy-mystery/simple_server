import select

class EventLoop:
    def __init__(self, name):
        self._name = name
        self._epoll_fd = select.epoll()
        self._fd_to_callback = {}
        self._idel_func = None

    def run(self):
        while True:
            events = self._epoll_fd.poll(1)
            if len(events) == 0:
                self.on_idel()
            for fd, event in events:
                print("{}: triger event {} fd {} ".format(self._name, event, fd))
                if fd in self._fd_to_callback:
                    self._fd_to_callback[fd][event](fd)
                else:
                    print("not found this file description{} event {}".format(fd, event))
                    return
    def register(self, fd, event, callback):
        print("{}, register fd {}, event {}".format(self._name, fd, event))
        self._epoll_fd.register(fd, event)
        if fd not in self._fd_to_callback:
            self._fd_to_callback[fd] = {}
        self._fd_to_callback[fd][event] = callback

    def set_idel(self, func):
        self._idel_func = func

    def on_idel(self):
        if self._idel_func is None:
            return
        self._idel_func()

    def unregister(self, fd):
        self._epoll_fd.unregister(fd)
        del self._fd_to_callback[fd]

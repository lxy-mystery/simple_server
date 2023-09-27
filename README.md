# simple_server

a simple multi process epoll server developed by python

## 环境安装
目前只支持linux环境下使用，python 版本号要求在 python 3.9 +
- 安装 python 环境
```bash
apt update;apt install python3.9 -y
```

## 使用说明

- 简单echo server 代码使用示例
```python
from acceptor import Acceptor

# 启动4个worker进程，启动一个监听9437端口的服务器
_server = Acceptor(4, ("0.0.0.0", 9437))
_server.start()
```

- 支持自定义Worker处理流程，只需要通过Worker类派生即可
```python
from acceptor import Acceptor
from worker import Worker

class MyWorker(Worker):
    def __init__(self, name, message_bus):
        super().__init__(name, message_bus)

    # 自定义请求数据处理
    def on_request(self, request_data):
        return (self._name + request_data.decode("utf-8")).encode("utf-8")

    def on_close(self, fd):
        print(f"worker:{self._name} connection:{fd} closed")
        return super().on_close(fd)

# 启动4个worker进程，启动一个监听9437端口的服务器
_server = Acceptor(4, ("0.0.0.0", 9437), MyWorker)
_server.start()
```

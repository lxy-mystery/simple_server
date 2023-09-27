# simple_server

a simple multi process epoll server developed by python

## ������װ
Ŀǰֻ֧��linux������ʹ�ã�python �汾��Ҫ���� python 3.9 +
- ��װ python ����
```bash
apt update;apt install python3.9 -y
```

## ʹ��˵��

- ��echo server ����ʹ��ʾ��
```python
from acceptor import Acceptor

# ����4��worker���̣�����һ������9437�˿ڵķ�����
_server = Acceptor(4, ("0.0.0.0", 9437))
_server.start()
```

- ֧���Զ���Worker�������̣�ֻ��Ҫͨ��Worker����������
```python
from acceptor import Acceptor
from worker import Worker

class MyWorker(Worker):
    def __init__(self, name, message_bus):
        super().__init__(name, message_bus)

    # �Զ����������ݴ���
    def on_request(self, request_data):
        return (self._name + request_data.decode("utf-8")).encode("utf-8")

    def on_close(self, fd):
        print(f"worker:{self._name} connection:{fd} closed")
        return super().on_close(fd)

# ����4��worker���̣�����һ������9437�˿ڵķ�����
_server = Acceptor(4, ("0.0.0.0", 9437), MyWorker)
_server.start()
```

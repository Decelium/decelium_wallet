import multiprocessing
import time
import uuid

class Vault:
    def __init__(self):
        self.data = {}

    def set_value(self, key, value):
        self.data[key] = value
        return 'success'

    def get_value(self, key):
        return self.data.get(key, None), 'success'

class Manager:
    def __init__(self):
        self.vault = Vault()

    def process_request(self, request_id, request_type, *args):
        if request_type == 'set':
            status = self.vault.set_value(*args)
        elif request_type == 'get':
            result, status = self.vault.get_value(*args)
            return request_id, result, status

        return request_id, status

def child_process(request_queue, response_queue):
    for i in range(10):
        request_id = uuid.uuid4()
        request_type = 'set'
        key = f'key{i}'
        value = f'value{i}'

        response_id, status = request_queue.apply_async(manager.process_request, args=(request_id, request_type, key, value)).get()
        assert response_id == request_id
        print(f'Child: Set request for {key} - {status}')

        request_id = uuid.uuid4()
        request_type = 'get'

        response_id, result, status = request_queue.apply_async(manager.process_request, args=(request_id, request_type, key)).get()
        assert response_id == request_id
        print(f'Child: Get request for {key} - {result} - {status}')

if __name__ == '__main__':
    manager = Manager()

    request_queue = multiprocessing.Pool(1)
    response_queue = multiprocessing.Queue()
    child_process(request_queue, response_queue)

import argparse
import threading
import sys
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from manager import ServerManager, ClientManager

def client_work(lock, data):
    with lock:
        data.value += 1
        print(data.value)

def main(argv):
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-s', '--server', action='store_true', help='start the ServerManager')
    group.add_argument('-c', '--client', action='store_true', help='start the ClientManager')
    parser.add_argument('--host', type=str, default='', help='the host to connect or bind to for IPC via Manager')
    parser.add_argument('--port', type=int, default=1337, help='the port to connect or bind to for IPC via Manager')
    parser.add_argument('--authkey', type=str, default='secret', help='process authentication key used for IPC via Manager')
    parser.add_argument('--processes', type=int, default='10', help='the number of processes to use')

    args = parser.parse_args()

    if args.server:
        ServerManager.register('Lock', threading.Lock, multiprocessing.managers.AcquirerProxy)
        ServerManager.register('Value', multiprocessing.managers.Value, multiprocessing.managers.ValueProxy)
        manager = ServerManager(args.host, args.port, bytearray(args.authkey, 'utf8'))
        input("ServerManager is listening. Press any key to exit.")
    elif args.client:
        ClientManager.register('Lock',threading.Lock, multiprocessing.managers.AcquirerProxy)
        ClientManager.register('Value', multiprocessing.managers.Value, multiprocessing.managers.ValueProxy)
        manager = ClientManager(args.host, args.port, bytearray(args.authkey, 'utf8'))
        lock = manager.Lock()
        data = manager.Value('i', 0)
        p = ProcessPoolExecutor(max_workers = args.processes)
        for i in range(100):
            p.submit(client_work, lock, data)

if __name__ == "__main__":
    main(sys.argv[1:])


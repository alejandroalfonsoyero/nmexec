import sys
import asyncio
from multiprocessing import Process
import signal
import socket
import struct
import pickle
import logging
import traceback
from typing import Optional, List

from .logger import get_logger
from .models.inverter import Inverter
from .models.yolo9 import Yolo9Model

models_map = {
    "inverter": Inverter,
    "yolo9": Yolo9Model
}


class Server:

    def __init__(self, host: str, port: int, backlog: int, logger: logging.Logger, worker_id: int = 0):
        self._host = host
        self._port = port
        self._backlog = backlog
        self._logger = logger
        self._proc: Optional[Process] = None
        self._worker_id = worker_id
        self._prefix = f"[Worker {self._worker_id}]"

    @property
    def proc(self) -> Optional[Process]:
        return self._proc

    async def reader_task(self, cli_name: str, reader: asyncio.StreamReader, buffer: asyncio.Queue) -> Optional[Exception]:
        try:
            while True:
                # Read first 4 bytes to get message size
                chunk = await reader.readexactly(4)
                if not chunk:
                    raise ConnectionError
                size = struct.unpack("!I", chunk)[0]
                data = b""
                while len(data) < size:
                    chunk = await reader.readexactly(size - len(data))
                    if not chunk:
                        raise ConnectionError
                    data += chunk

                await buffer.put(data)
        except asyncio.CancelledError:
            self._logger.info(f"{self._prefix} Reader task cancelled")
        except asyncio.IncompleteReadError:
            self._logger.info(f"{self._prefix} Client disconnected")
        except ConnectionError:
            self._logger.info(f"{self._prefix} Client disconnected")
        except asyncio.TimeoutError:
            self._logger.info(f"{self._prefix} Client timeout")
        except Exception as err:
            print(type(err))
            traces = traceback.format_exception(*sys.exc_info())[1:]
            for trace in traces:
                self._logger.error(f"{self._prefix} {trace}")
                self._logger.error(f"{self._prefix} {err}")
        finally:
            await buffer.put(None)

    async def processor_task(self, cli_name: str, writer: asyncio.StreamWriter, buffer: asyncio.Queue):
        model = None
        while True:
            try:
                data = buffer.get_nowait()
                if data is None:
                    break
                if model is None:
                    conf = pickle.loads(data)
                    model_name = conf["model_name"]
                    model_kwargs = conf["model_kwargs"]
                    model = models_map[model_name](**model_kwargs)
                else:
                    x = pickle.loads(data)
                    y = model.execute(x)
                    response = pickle.dumps(y)
                    writer.write(struct.pack("!I", len(response)))
                    writer.write(response)
                    await writer.drain()
            except asyncio.QueueEmpty:
                await asyncio.sleep(0.001)

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        addr = writer.get_extra_info("peername")
        self._logger.info(f"{self._prefix} Client connected {addr}")
        buffer = asyncio.Queue()

        await asyncio.gather(
            self.reader_task(addr, reader, buffer),
            self.processor_task(addr, writer, buffer)
        )

    async def _start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        server_socket.bind((self._host, self._port))
        server_socket.listen(self._backlog)

        server = await asyncio.start_server(self.handle_client, sock=server_socket)
        addr = server_socket.getsockname()
        self._logger.info(f"{self._prefix} Server started on {addr}")

        async with server:
            await server.serve_forever()

    def run(self) -> Process:
        def _wrapper():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._start_server())

        self._proc = Process(target=_wrapper)
        self._proc.start()
        return self._proc


class Cluster:
    def __init__(self, host: str = "0.0.0.0", port: int = 5000, backlog: int = 128):
        self.workers: List[Server] = []
        self.host = host
        self.port = port
        self.backlog = backlog
        self.logger = get_logger("NMExec")
        self.logger.setLevel(logging.INFO)
        signal.signal(signal.SIGINT, self.cleanup)

    def cleanup(self, signum, frame):
        for worker in self.workers:
            if isinstance(worker.proc, Process):
                worker.proc.kill()

    def run(self, workers: int):
        self.logger.info("Starting cluster")
        procs = []
        for worker_id in range(workers):
            worker = Server(self.host, self.port, self.backlog, self.logger, worker_id)
            self.workers.append(worker)
            procs.append(worker.run())

        for proc in procs:
            proc.join()

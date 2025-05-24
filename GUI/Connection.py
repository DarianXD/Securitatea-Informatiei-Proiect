import threading
import queue
import socket

from AES import aes_ecb, aes_expand_key, aes_free_key, AES
from Types import File, FileRequest, FileConfirmation, FileSendConfirmation, FileRecvConfirmation, FileSendProgress, FileRecvProgress, EncryptionError, DecryptionError, EncryptionKeyError

_MESSAGE_TYPE = 0
_FILE_TYPE = 1
_FILE_REQUEST_TYPE = 2
_FILE_RESPONSE_TYPE = 3

class ConnectionWorker(threading.Thread):
    def __init__(self, ip, port, mode, on_success, on_error, on_close):
        super().__init__(daemon=True)
        self.ip = ip
        self.port = port
        self.mode = mode
        self.on_success = on_success
        self.on_error = on_error
        self.on_close = on_close
        
        self.running = threading.Event()
        self.running.set()

    def negotiate(self, sock: socket.socket):
        # Placeholder for negotiation logic
        # Uses Diffie-Hellman key exchange
        # p and g are stored in a file
        # each transmits over the socket the secret number
        # and receives the other party's secret number
        # calculate the sheared secret
        # use it in a Key Derivation Function (KDF)
        # algoritm could also be stored in the file
        return (AES.AES_128, [0x00] * 16)

    def run(self):
        try:
            addr = None
            sock = None
            if self.mode == "client":
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                sock.connect((self.ip, int(self.port)))
                addr = sock.getpeername()
            else:
                server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server_sock.bind((self.ip, int(self.port)))
                server_sock.listen(1)
                server_sock.settimeout(0.1)
                while self.running.is_set():
                    try:
                        sock, _ = server_sock.accept()
                        addr = sock.getpeername()
                        break

                    except socket.timeout:
                        continue

                server_sock.close()

            if sock is not None:
                alg, key = self.negotiate(sock)
                key = aes_expand_key(alg, key)
                if key is None:
                    raise EncryptionKeyError()

                conn = Connection(sock, self.on_error, self.on_close, alg, key)
                self.on_success(conn, addr)
                
        except Exception as e:
            self.on_error(str(e))

    def stop(self):
        if self.running.is_set():
            self.running.clear()
            self.join()

class Connection:
    def __init__(self, sock: socket.socket, on_error, on_close, alg, key):
        self.sock = sock
        self.key = key
        self.alg = alg
        
        self.recv_queue = queue.Queue()
        self.send_queue = queue.Queue()

        self.send_file_queue = queue.Queue()

        self.write_file_queue = queue.Queue()

        self.running = threading.Event()
        self.sock.settimeout(0.1)
        self.running.set()

        self.send_lock = threading.Lock()
        self.file_accept = threading.Event()
        self.file_accept_lock = threading.Lock()
        self.file_accept_flag = False

        self.current_file = None
        self.current_file_lock = threading.Lock()

        self.current_file_size = 0
        self.current_file_size_lock = threading.Lock()
    
        self.recv_size = 1500
        self.file_chunk_size = 100000000
        self.file_chunk_send_size = 10000

        self.file_progress_info_interval = 1000000

        self.on_error = on_error
        self.on_close = on_close

        self.recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
        self.send_thread = threading.Thread(target=self._send_loop, daemon=True)
        self.send_file_thread = threading.Thread(target=self._send_file_loop, daemon=True)
        self.write_file_thread = threading.Thread(target=self._write_file_loop, daemon=True)

        self.recv_thread.start()
        self.send_thread.start()
        self.send_file_thread.start()
        self.write_file_thread.start()

    @property
    def receiving_file(self):
        with self.current_file_lock:
            return self.current_file is not None
        
    @property
    def sending_file(self):
        with self.file_accept_lock:
            return self.file_accept_flag

    def _recv_loop(self):
        data = b''
        while self.running.is_set():
            try:
                recv = self.sock.recv(self.recv_size)
                if not recv:
                    self.on_close()
                    break

                data += recv

                while True:
                    packet_type = self._check_packet(data)
                    if packet_type is None:
                        break

                    if packet_type == _MESSAGE_TYPE:
                        val, size = self._unpackage_data(data)
                        if size == 0:
                            break

                        self.recv_queue.put(val)
                        data = data[size:]

                    elif packet_type == _FILE_TYPE:
                        val, size, last_chunk = self._unpackage_file(data)
                        if size == 0:
                            break

                        self.write_file_queue.put((val, last_chunk))
                        data = data[size:]

                    elif packet_type == _FILE_REQUEST_TYPE:
                        file_request, size = self._unpackage_file_request(data)
                        if size == 0:
                            break

                        with self.current_file_size_lock:
                            self.current_file_size = file_request.size

                        self.recv_queue.put(file_request)
                        data = data[size:]

                    elif packet_type == _FILE_RESPONSE_TYPE:
                        flag, size = self._unpackage_file_response(data)

                        with self.file_accept_lock:
                            self.file_accept_flag = flag

                        self.file_accept.set()
                        data = data[size:]
                        

            except socket.timeout:
                continue

            except Exception as e:
                self.on_error(str(e))
                break
        
        self.running.clear()

    def _send_loop(self):
        while self.running.is_set():
            try:
                data = self.send_queue.get(timeout=0.1)
                if data is None:
                    continue

                if isinstance(data, FileConfirmation):
                    data = self._package_file_response(data.ok)
                else:
                    data = self._package_data(data)

                with self.send_lock:
                    self.sock.sendall(data)

            except queue.Empty:
                continue

            except socket.timeout:
                continue

            except Exception as e:
                self.on_error(str(e))
                break

        self.running.clear()

    def _send_file_loop(self):
        while self.running.is_set():
            try:
                file = self.send_file_queue.get(timeout=0.1)
                if file is None:
                    continue

                request = self._package_file_request(file)

                with self.send_lock:
                    self.sock.sendall(request)

                self.file_accept.wait()
                self.file_accept.clear()

                flag = False
                with self.file_accept_lock:
                    flag = self.file_accept_flag

                if flag:
                    self.recv_queue.put(FileConfirmation(True))

                    file_send = False
                    total_sent = 0
                    with open(file.path, "rb") as f:
                        while self.running.is_set():
                            file_chunk = f.read(self.file_chunk_size)
                            if not file_chunk:
                                break

                            send_chunks = [file_chunk[i:i+self.file_chunk_send_size] for i in range(0, len(file_chunk), self.file_chunk_send_size)]

                            for chunk in send_chunks:
                                last = not len(chunk) == self.file_chunk_send_size
                                data = self._package_file(chunk, last)

                                if last:
                                    file_send = True

                                with self.send_lock:
                                    self.sock.sendall(data)
                                
                                total_sent += len(chunk)
                                if total_sent % self.file_progress_info_interval == 0:
                                    self.recv_queue.put(FileSendProgress(total_sent, file.size))

                    with self.file_accept_lock:
                        self.file_accept_flag = False

                    self.recv_queue.put(FileSendConfirmation(file_send))

                else:
                    self.recv_queue.put(FileConfirmation(False))
                
            except queue.Empty:
                continue

            except socket.timeout:
                continue

            except Exception as e:
                self.on_error(str(e))
                break

        self.running.clear()

    def _write_file_loop(self):
        while self.running.is_set():
            try:
                path = None
                with self.current_file_lock:
                    path = self.current_file

                total_size = 0
                with self.current_file_size_lock:
                    total_size = self.current_file_size

                if path is None:
                    continue
                
                file_saved = False
                total_saved = 0
                data = b''
                with open(path, "ab") as f:
                    while self.running.is_set():
                        try:
                            val = self.write_file_queue.get(timeout=0.1)
                            if val is None:
                                continue

                            val, last = val

                            data += val
                            
                            if len(data) >= self.file_chunk_size:
                                f.write(data)
                            
                            total_saved += len(val)
                            if total_saved % self.file_progress_info_interval == 0:
                                self.recv_queue.put(FileRecvProgress(total_saved, total_size))

                            if last:
                                with self.current_file_lock:
                                    self.current_file = None

                                file_saved = True
                                break

                        except queue.Empty:
                            continue

                self.recv_queue.put(FileRecvConfirmation(file_saved))

            except Exception as e:
                self.on_error(str(e))
                break
        
    def _package_data(self, data: bytes):
        data = self._encrypt(data)

        header = bytearray(1)
        header.extend(len(data).to_bytes(8, 'big'))
        header = self._encrypt(header)

        return header + data
    
    def _package_file(self, data: bytes, last_chunk: bool):
        data = self._encrypt(data)

        header = bytearray(1)
        header[0] |= 0b10000000

        if not last_chunk:
            header[0] |= 0b01000000

        header.extend(len(data).to_bytes(8, 'big'))
        header = self._encrypt( header)

        return header + data
    
    def _package_file_request(self, file: File):
        data = self._encrypt(file.name.encode('utf-8'))

        header = bytearray(1)
        header[0] |= 0b10100000
        header.extend(file.size.to_bytes(8, 'big'))
        header.extend(len(data).to_bytes(6, 'big'))
        header = self._encrypt(header)

        return header + data
    
    def _package_file_response(self, response: bool):
        header = bytearray(1)
        header[0] |= 0b10010000

        if response:
            header[0] |= 0b01000000

        header = self._encrypt(header)
        return header
        
    def _check_packet(self, packet: bytes):
        if len(packet) < 16:
            return None

        header = self._decrypt(packet[:16])

        if not (header[0] & 0b10000000):
            return _MESSAGE_TYPE
        else:
            if header[0] & 0b00100000:
                return _FILE_REQUEST_TYPE
            
            if header[0] & 0b00010000:
                return _FILE_RESPONSE_TYPE
            
            return _FILE_TYPE
        
    def _unpackage_data(self, packet: bytes):
        if len(packet) < 16:
            return None, 0

        header = self._decrypt(packet[:16])
        size = int.from_bytes(header[1:9], 'big') + 16

        if len(packet) < size:
            return None, 0

        data = self._decrypt(packet[16:size])
        return data, size
    
    def _unpackage_file(self, packet: bytes):
        if len(packet) < 16:
            return None, 0, False

        header = self._decrypt(packet[:16])
        size = int.from_bytes(header[1:9], 'big') + 16

        if len(packet) < size:
            return None, 0, False
        
        last_chunk = not (header[0] & 0b01000000)
        data = self._decrypt(packet[16:size])
        return data, size, last_chunk
    
    def _unpackage_file_request(self, packet: bytes):
        if len(packet) < 16:
            return None, 0

        header = self._decrypt(packet[:16])
        file_size = int.from_bytes(header[1:9], 'big')
        size = int.from_bytes(header[9:15], 'big') + 16

        if len(packet) < size:
            return None, 0

        name = self._decrypt(packet[16:size]).decode('utf-8')
        return FileRequest(name, file_size), size
    
    def _unpackage_file_response(self, packet: bytes):
        if len(packet) < 16:
            return None, 0

        header = self._decrypt(packet[:16])

        return header[0] & 0b01000000, 16

    def send(self, data: bytes):
        self.send_queue.put(data)

    def send_file(self, file: File):
        self.send_file_queue.put(file)

    def recv(self):
        try:
            return self.recv_queue.get_nowait()
        except queue.Empty:
            return None
        
    def accept_file(self, path: str, accept: bool = True):
        confirm = FileConfirmation(accept)
        self.send_queue.put(confirm)

        if confirm.ok:
            with self.current_file_lock:
                if self.current_file is not None:
                    raise Exception("File download error")

                self.current_file = path

    def _encrypt(self, data: bytes):
        val = aes_ecb(self.alg, self.key, data)
        if len(val) == 0:
            raise EncryptionError()
        
        return val
        
    def _decrypt(self, data: bytes):
        val = aes_ecb(self.alg, self.key, data, decrypt=True)
        if len(val) == 0:
            raise DecryptionError()
        
        return val

    def close(self):
        if self.running.is_set():
            self.running.clear()

            self.recv_thread.join()
            self.send_thread.join()

            self.send_file_thread.join()
            self.write_file_thread.join()

            self.sock.close()

            aes_free_key(self.key)

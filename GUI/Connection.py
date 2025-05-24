import threading
import queue
import socket

from AES import aes_ecb, AES
from Types import File

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
        self.running = threading.Event()
        self.sock.settimeout(0.1)
        self.running.set()
    
        self.packet_size = 1500

        self.on_error = on_error
        self.on_close = on_close
        self.recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
        self.send_thread = threading.Thread(target=self._send_loop, daemon=True)
        self.recv_thread.start()
        self.send_thread.start()

    def _recv_loop(self):
        data = b''
        while self.running.is_set():
            try:
                data += self.sock.recv(self.packet_size)
                if not data:
                    self.on_close()
                    break

                while True:
                    val, size = self._unpackage_data(data)
                    if size == 0:
                        break

                    self.recv_queue.put(val)
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

                data = self._package_data(data)
                data = [data[i:i + self.packet_size] for i in range(0, len(data), self.packet_size)]

                for val in data:
                    self.sock.sendall(val)

            except queue.Empty:
                continue

            except socket.timeout:
                continue

            except Exception as e:
                self.on_error(str(e))
                break

        self.running.clear()

    def _package_data(self, data: bytes | File):
        header = bytearray(1)

        message = data
        filename = None
        file = False
        if isinstance(data, File):
            message = data.data
            filename = data.name
            file = True
 
        header[0] |= 0b10000000 if file else 0b00000000

        message = aes_ecb(self.alg, self.key, message) if message is not None else b''
        filename = aes_ecb(self.alg, self.key, filename) if filename is not None else b''

        header.extend(len(message).to_bytes(8, 'big') if message is not None else b'\x00' * 8)
        header.extend(len(filename).to_bytes(6, 'big') if filename is not None else b'\x00' * 6)

        header = aes_ecb(self.alg, self.key, header)

        return header + message + filename
        
    def _unpackage_data(self, packet: bytes):
        if (len(packet) < 16):
            return None, 0
        
        header = aes_ecb(self.alg, self.key, packet[:16], decrypt=True)
        
        file = header[0] & 0b10000000 != 0

        message_len = int.from_bytes(header[1:9], 'big')
        filename_len = int.from_bytes(header[9:15], 'big')
        packet_len = 16 + message_len + filename_len

        if len(packet) < packet_len:
            return None, 0
        
        message = aes_ecb(self.alg, self.key, packet[16:16 + message_len], decrypt=True)
        filename = aes_ecb(self.alg, self.key, packet[16 + message_len:16 + message_len + filename_len], decrypt=True)

        if message == b'':
            message = None

        if filename == b'':
            filename = None

        if file:
            return File(filename, message), packet_len
        
        return message, packet_len

    def send(self, data: bytes):
        self.send_queue.put(data)

    def recv(self):
        try:
            return self.recv_queue.get_nowait()
        except queue.Empty:
            return None

    def close(self):
        if self.running.is_set():
            self.running.clear()
            self.recv_thread.join()
            self.send_thread.join()
            self.sock.close()

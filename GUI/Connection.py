import threading
import queue
import socket

from AES import aes_ecb, AES

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

        self.on_error = on_error
        self.on_close = on_close
        self.recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
        self.send_thread = threading.Thread(target=self._send_loop, daemon=True)
        self.recv_thread.start()
        self.send_thread.start()

    def _recv_loop(self):
        while self.running.is_set():
            try:
                data = self.sock.recv(5000)
                if not data:
                    self.on_close()
                    break

                data = aes_ecb(self.alg, self.key, data, decrypt=True)

                self.recv_queue.put(data)

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

                data = aes_ecb(self.alg, self.key, data)

                self.sock.sendall(data)

            except queue.Empty:
                continue

            except socket.timeout:
                continue

            except Exception as e:
                self.on_error(str(e))
                break

        self.running.clear()

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

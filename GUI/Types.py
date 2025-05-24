class File:
    def __init__(self, path, name, size):
        self.path = path
        self.name = name
        self.size = size

class FileRequest:
    def __init__(self, name, size):
        self.name = name
        self.size = size

class FileConfirmation:
    def __init__(self, ok):
        self.ok = ok

class FileSendConfirmation:
    def __init__(self, ok):
        self.ok = ok

class FileRecvConfirmation:
    def __init__(self, ok):
        self.ok = ok

class FileSendProgress:
    def __init__(self, sent, total):
        self.sent = sent
        self.total = total

class FileRecvProgress:
    def __init__(self, received, total):
        self.received = received
        self.total = total

class EncryptionError(Exception):
    def __init__(self):
        super().__init__("Encryption error")

class DecryptionError(Exception):
    def __init__(self):
        super().__init__("Decryption error")

class EncryptionKeyError(Exception):
    def __init__(self):
        super().__init__("Encryption key error")

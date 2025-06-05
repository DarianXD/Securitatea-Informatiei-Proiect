import ctypes
from ctypes import c_size_t, c_bool, c_void_p, c_int, POINTER, c_uint8, c_uint32
from enum import IntEnum

# included library fo arm64 Darwin
# compiled on macOS 15.5 (24F74)
libaes = ctypes.CDLL('./libaes.dylib')

class AES(IntEnum):
    AES_128 = 0
    AES_192 = 1
    AES_256 = 2

word = c_uint32
byte = c_uint8

AES_key = POINTER(word)

libaes.AES_ECB.restype = c_size_t
libaes.AES_ECB.argtypes = [
    c_int,                # AES alg
    AES_key,              # const AES_key expanded_key
    POINTER(byte),        # const byte *input
    POINTER(byte),        # byte *output
    c_size_t,             # inputSize
    c_size_t,             # outputSize
    c_bool                # decrypt
]

libaes.AES_expand_key.restype = AES_key
libaes.AES_expand_key.argtypes = [
    c_int,         # AES alg
    POINTER(word)  # const word *key
]

libaes.AES_free_key.restype = None
libaes.AES_free_key.argtypes = [
    POINTER(AES_key)  # AES_key *key
]

def aes_ecb(alg, expanded_key, input_bytes, decrypt=False):
    input_array = (byte * len(input_bytes))(*input_bytes)
    output_array = (byte * (len(input_bytes) + 16))()

    out_size = libaes.AES_ECB(
        alg,
        expanded_key,
        input_array,
        output_array,
        len(input_array),
        len(output_array),
        decrypt
    )

    return bytes(output_array[:out_size])

def aes_expand_key(alg, key):
    key_len = 16 if alg == AES.AES_128 else 24 if alg == AES.AES_192 else 32
    key_array = (word * key_len)(*key)

    return libaes.AES_expand_key(
        alg, 
        key_array
    )



def aes_free_key(expanded_key):
    key_ptr = ctypes.pointer(expanded_key)

    libaes.AES_free_key(
        key_ptr
    )

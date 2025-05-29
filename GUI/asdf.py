from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

def generate_vector(key_bytes, plaintext_bytes):
    cipher = AES.new(key_bytes, AES.MODE_ECB)
    padded = pad(plaintext_bytes, 16)
    ciphertext = cipher.encrypt(padded)
    return {
        "key": key_bytes.hex(),
        "plaintext": plaintext_bytes.hex(),
        "ciphertext": ciphertext.hex()
    }

key = b'\x01\x23\x45\x67\x89\xab\xcd\xef\xfe\xdc\xba\x98\x76\x54\x32\x10'

texts = [
    b"Test vector 1.",
    b"Another test vector, slightly longer!",
    b"Short",
    b"Exactly sixteen!!",
    b"Padding test with 15 bytes.",
    b"Chestii random",
    b"Darian",
    b"asdf qwerty 1234 zxcv",
    b"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla malesuada.",
    b'AES'
]

vectors = [generate_vector(key, t) for t in texts]

for i, v in enumerate(vectors):
    print(f"Vector {i+1}:")
    print(f"Key       : {v['key']}")
    print(f"Plaintext : {v['plaintext']}")
    print(f"Ciphertext: {v['ciphertext']}\n")

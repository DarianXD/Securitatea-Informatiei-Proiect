from AES import aes_ecb, aes_expand_key, aes_free_key, AES
from Types import File, FileRequest, FileConfirmation, FileSendConfirmation, FileRecvConfirmation, FileSendProgress, FileRecvProgress, EncryptionError, DecryptionError, EncryptionKeyError

test_vectors = [
    # AES-128
    {
        "key": bytes.fromhex("0123456789abcdeffedcba9876543210"),
        "plaintext": bytes.fromhex("5465737420766563746f7220312e"),
        "ciphertext": bytes.fromhex("d196001966f9afc9894ade73a9b7b3df")
    }, {
        "key": bytes.fromhex("0123456789abcdeffedcba9876543210"),
        "plaintext": bytes.fromhex("416e6f74686572207465737420766563746f722c20736c696768746c79206c6f6e67657221"),
        "ciphertext": bytes.fromhex("25a1c31fd4350087cec66b0122210df6733d5921dc4365e8117516724c189bc9f8c0b5fcb373128252c65d9b926df83d")
    }, {
        "key": bytes.fromhex("0123456789abcdeffedcba9876543210"),
        "plaintext": bytes.fromhex("53686f7274"),
        "ciphertext": bytes.fromhex("cfa0811d28f34a80d7f02888e43298af")
    }, {
        "key": bytes.fromhex("0123456789abcdeffedcba9876543210"),
        "plaintext": bytes.fromhex("45786163746c79207369787465656e2121"),
        "ciphertext": bytes.fromhex("2ed190a3bb5804d28f23dc5293b05b4fab3ee5fe7ca47cb3b2da19f0741c5d82")
    }, {
        "key": bytes.fromhex("0123456789abcdeffedcba9876543210"),
        "plaintext": bytes.fromhex("50616464696e67207465737420776974682031352062797465732e"),
        "ciphertext": bytes.fromhex("3a368dc5fa9b1cac739707eef3030e127088b67a55952d27251150d69cc789d0")
    }, {
        "key": bytes.fromhex("0123456789abcdeffedcba9876543210"),
        "plaintext": bytes.fromhex("436865737469692072616e646f6d"),
        "ciphertext": bytes.fromhex("5a93c91b3f601759482a1d38a0aa2c0d")
    }, {
        "key": bytes.fromhex("0123456789abcdeffedcba9876543210"),
        "plaintext": bytes.fromhex("44617269616e"),
        "ciphertext": bytes.fromhex("e3075c4b6ba6f640f24324cfd209620a")
    }, {
        "key": bytes.fromhex("0123456789abcdeffedcba9876543210"),
        "plaintext": bytes.fromhex("61736466207177657274792031323334207a786376"),
        "ciphertext": bytes.fromhex("d6ca499ea5cfd8bde1739bf34a843b75e97c3bf35966014d12c68dcaebaa99c5")
    }, {
        "key": bytes.fromhex("0123456789abcdeffedcba9876543210"),
        "plaintext": bytes.fromhex("4c6f72656d20697073756d20646f6c6f722073697420616d65742c20636f6e73656374657475722061646970697363696e6720656c69742e204e756c6c61206d616c6573756164612e"),
        "ciphertext": bytes.fromhex("bd091d4529374b6e79b40e4bc0cd5e7d742bb4eb89c9ef2e5f201ec7831d863a47f872917b52b856652610c8c0859d85da66ad8666f7a72786e058154a48aa6206384c91853ccecaa3674e7b2a2bd9f0")
    }, {
        "key": bytes.fromhex("0123456789abcdeffedcba9876543210"),
        "plaintext": bytes.fromhex("414553"),
        "ciphertext": bytes.fromhex("6bf80c7d97db27cbaa765dd41541ae69")
    },
]


def test_aes_implementation():
    for vector in test_vectors:
        key = vector["key"]
        plaintext = vector["plaintext"]
        expected_ciphertext = vector["ciphertext"]

        # Alegem algoritmul AES în funcție de lungimea cheii
        if len(key) == 16:
            alg = AES.AES_128
        elif len(key) == 24:
            alg = AES.AES_192
        else:
            alg = AES.AES_256

        # Extindem cheia (cheie internă pentru AES)
        expanded_key = aes_expand_key(alg, list(key))

        # Criptăm plaintextul
        ciphertext = aes_ecb(alg, expanded_key, plaintext, decrypt=False)
        # Verificăm dacă criptarea corespunde vectorului de test
        assert ciphertext == expected_ciphertext, f"Encrypt failed for key length {len(key)*8}"

        # Decriptăm ciphertextul obținut
        decrypted = aes_ecb(alg, expanded_key, expected_ciphertext, decrypt=True)

        # Verificăm dacă decriptarea readuce textul original
        assert decrypted == plaintext, f"Decrypt failed for key length {len(key)*8}"

        # Eliberăm cheia extinsă
        aes_free_key(expanded_key)
    
    print("All AES tests passed successfully!")

if __name__ == "__main__":
    test_aes_implementation()

#include <stdlib.h>
#include "AES.h"

word *KeyExpansion(AES alg, const word *key);

void AESBlock(AES alg, const word *w, const byte *input, byte *output, bool decrypt);
size_t PKCS7(const byte *input, byte *output, size_t inputSize, size_t outputSize, bool unpad);

size_t AES_ECB(AES alg, const word *key, const byte *input, byte *output, size_t inputSize, size_t outputSize, bool decrypt) {
    if (!input || !output || !key || !inputSize || !outputSize) {
        return 0;
    }

    byte *inputAES = (byte *)input;
    size_t size = inputSize;
    if (!decrypt) {
        // Encryption padding
        inputAES = output;
        if (!(size = PKCS7(input, inputAES, inputSize, outputSize, false))) {
            return 0;
        }
    } else if (size % 16) {
        return 0;
    }

    word *expanded_key = KeyExpansion(alg, key);
    if (!expanded_key) {
        return 0;
    }

    for (size_t block = 0; block < size; block += 16) {
        AESBlock(alg, expanded_key, inputAES + block, output + block, decrypt);
    }

    free(expanded_key);

    if (decrypt) {
        // Decryption unpadding
        if (!(size = PKCS7(output, output, size, outputSize, true))) {
            return 0;
        }
    }

    return size;
}

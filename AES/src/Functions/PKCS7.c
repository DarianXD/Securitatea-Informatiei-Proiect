#include <string.h>
#include <stdbool.h>
#include "AES.h"

size_t PKCS7_pad(const byte *input, byte *output, size_t inputSize, size_t outputSize);
size_t PKCS7_unpad(const byte *input, byte *output, size_t inputSize, size_t outputSize);

size_t PKCS7(const byte *input, byte *output, size_t inputSize, size_t outputSize, bool unpad) {
    if (!unpad) {
        return PKCS7_pad(input, output, inputSize, outputSize);
    } else {
        return PKCS7_unpad(input, output, inputSize, outputSize);
    }
}

size_t PKCS7_pad(const byte *input, byte *output, size_t inputSize, size_t outputSize) {
    byte pad = 16 - (inputSize % 16);
    if (!pad) {
        pad = 16;
    }

    if (inputSize + pad > outputSize) {
        return 0;
    }

    memcpy(output, input, inputSize);
    memset(output + inputSize, pad, pad);

    return inputSize + pad;
}

size_t PKCS7_unpad(const byte *input, byte *output, size_t inputSize, size_t outputSize) {
    if (inputSize % 16) {
        return 0;
    }

    byte pad = input[inputSize - 1];
    if (!pad || pad > 16) {
        return 0;
    }

    if (inputSize - pad > outputSize) {
        return 0;
    }

    for (byte i = 1; i <= pad; i++) {
        if (input[inputSize - i] != pad) {
            return 0;
        }
    }

    memcpy(output, input, inputSize - pad);

    return inputSize - pad;
}

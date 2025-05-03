#include <stdlib.h>
#include "AES.h"

word *KeyExpansion(AES alg, const word *key);

void AESBlock(AES alg, const word *w, const byte *input, byte *output, bool decrypt);

bool AES_ECB(AES alg, const word *key, const byte *input, byte *output, size_t size, bool decrypt) {
    if (size % 16 != 0) {
        return false;
    }

    word *expanded_key = KeyExpansion(alg, key);
    if (!expanded_key) {
        return false;
    }

    for (size_t block = 0; block < size; block += 16) {
        AESBlock(alg, expanded_key, input + block, output + block, decrypt);
    }

    free(expanded_key);
    return true;
}

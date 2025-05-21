#ifndef AES_H
#define AES_H

#include <stddef.h>
#include <stdbool.h>

#include "Types.h"

typedef enum {
    AES_128 = 0,
    AES_192 = 1,
    AES_256 = 2
} AES;

size_t AES_ECB(AES alg, const word *key, const byte *input, byte *output, size_t inputSize, size_t outputSize, bool decrypt);

#endif /* AES_H */

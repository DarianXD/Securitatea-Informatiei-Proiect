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

typedef word* AES_key;

size_t AES_ECB(AES alg, const AES_key expanded_key, const byte *input, byte *output, size_t inputSize, size_t outputSize, bool decrypt);

AES_key AES_expand_key(AES alg, const word *key);
void AES_free_key(AES_key *key);

#endif /* AES_H */

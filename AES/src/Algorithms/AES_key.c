#include <stdlib.h>
#include "AES.h"

word *KeyExpansion(AES alg, const word *key);

AES_key AES_expand_key(AES alg, const word *key) {
    if (!key) {
        return NULL;
    }

    return KeyExpansion(alg, key);
}

void AES_free_key(AES_key *key) {
    if (key && *key) {
        free(*key);
        *key = NULL;
    }
}

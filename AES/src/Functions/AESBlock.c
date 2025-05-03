#include <stdbool.h>
#include "AES.h"

extern const byte Nr_array[];

word *KeyExpansion(AES alg, const word *key);

void Cipher(byte val[4][4], byte Nr, const word *w);
void InvCipher(byte val[4][4], byte Nr, const word *w);

void AESBlock(AES alg, const word *w, const byte *input, byte *output, bool decrypt) {
    /* variables based on selected algorithm */
    byte Nr = Nr_array[alg];

    byte state[4][4];

    for (byte row = 0; row < 4; row++) {
        for (byte col = 0; col < 4; col++) {
            state[row][col] = input[row + col * 4];
        }
    }

    if (!decrypt) {
        Cipher(state, Nr, w);
    } else {
        InvCipher(state, Nr, w);
    }

    for (byte row = 0; row < 4; row++) {
        for (byte col = 0; col < 4; col++) {
            output[row + col * 4] = state[row][col];
        }
    }
}

#include "Types.h"

void AddRoundKey(byte val[4][4], const word *w, byte round) {
    for (byte c = 0; c < 4; c++) {
        word roundKey = w[4 * round + c];
        for (byte r = 0; r < 4; r++) {
            val[r][c] ^= (roundKey >> (8 * (3 - r))) & 0xFF; // Extrage byte-ul corespunzător
        }
    }
}
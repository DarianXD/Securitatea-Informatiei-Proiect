#include "Types.h"

void AddRoundKey(byte val[4][4], const word *w, byte round);
void ShiftRows(byte val[4][4]);
void SubBytes(byte val[4][4]);
void MixColumns(byte val[4][4]);

void Cipher(byte val[4][4], byte Nr, const word *w) {
    AddRoundKey(val, w, 0);
    for (byte round = 1; round < Nr; round++) {
        SubBytes(val);
        ShiftRows(val);
        MixColumns(val);
        AddRoundKey(val, w, round);
    }
    SubBytes(val);
    ShiftRows(val);
    AddRoundKey(val, w, Nr);
}

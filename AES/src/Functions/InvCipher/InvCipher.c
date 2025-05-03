#include "Types.h"

void AddRoundKey(byte val[4][4], const word *w, byte round);

void InvShiftRows(byte val[4][4]);
void InvSubBytes(byte val[4][4]);
void InvMixColumns(byte val[4][4]);

void InvCipher(byte val[4][4], byte Nr, const word *w) {
    AddRoundKey(val, w, Nr);
    for (byte round = Nr - 1; round > 0; round--) {
        InvShiftRows(val);
        InvSubBytes(val);
        AddRoundKey(val, w, round);
        InvMixColumns(val);
    }
    InvShiftRows(val);
    InvSubBytes(val);
    AddRoundKey(val, w, 0);
}

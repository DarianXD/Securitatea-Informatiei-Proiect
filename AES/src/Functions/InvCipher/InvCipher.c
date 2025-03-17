#include "Types.h"

void AddRoundKey(byte val[4][4], word w);
void InvShiftRows(byte val[4][4]);
void InvSubBytes(byte val[4][4]);
void InvMixColumns(byte val[4][4]);

void InvCipher(byte val[4][4], byte Nr, byte *w) {
    AddRoundKey(val, w[Nr]);
    for (byte round = Nr - 1; round >= 1; round--) {
        InvShiftRows(val);
        InvSubBytes(val);
        AddRoundKey(val, w[round]);
        InvMixColumns(val);
    }
    InvShiftRows(val);
    InvSubBytes(val);
    AddRoundKey(val, w[0]);
}

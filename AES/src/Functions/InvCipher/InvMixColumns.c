#include "Types.h"

byte GFTimes(byte b, byte c);

void InvMixColumns(byte val[4][4]) {
    byte table[4][4] = {
        {0x0e, 0x0b, 0x0d, 0x09},
        {0x09, 0x0e, 0x0b, 0x0d},
        {0x0d, 0x09, 0x0e, 0x0b},
        {0x0b, 0x0d, 0x09, 0x0e}
    };

    for (byte col = 0; col < 4; col++) {
        byte result[4] = {0};
        for (byte row = 0; row < 4; row++) {
            for (byte i = 0; i < 4; i++) {
                result[row] ^= GFTimes(val[i][col], table[row][i]);
            }
        }
    }
}

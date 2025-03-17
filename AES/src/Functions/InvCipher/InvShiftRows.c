#include "Types.h"

void InvShiftRows(byte val[4][4]) {
    for (byte row = 1; row < 4; row++) {
        for (byte shift = 0; shift < row; shift++) {
            byte col = 3, temp = val[row][col];
            for (;col > 0; col--) {
                val[row][col] = val[row][col - 1];
            }

            val[row][col] = temp;
        }
    }
}

#include "Types.h"

byte InvSBox(byte b);

void InvSubBytes(byte val[4][4]) {
    for (byte row = 0; row < 4; row++) {
        for (byte col = 0; col < 4; col++) {
            val[row][col] = InvSBox(val[row][col]);
        }
    }
}

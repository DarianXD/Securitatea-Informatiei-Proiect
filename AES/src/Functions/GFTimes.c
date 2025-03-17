#include "Types.h"

byte XTimes(byte b);

byte GFTimes(byte b, byte c) {
    byte result = 0;
    for (byte bit = 0; bit < 8; bit++) {
        if (!(c & 1)) {
            continue;   
        }

        byte val = b;
        for (byte times = 0; times < bit; times++) {
            val = XTimes(val);
        }

        result ^= val;
    }

    return result;
}

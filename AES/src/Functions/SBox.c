#include "Types.h"

extern const byte S_Box[16][16];

byte SBox(byte b) {
    return S_Box[b >> 4][b & 0x0f];
}

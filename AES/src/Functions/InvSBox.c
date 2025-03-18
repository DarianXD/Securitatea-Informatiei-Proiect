#include "Types.h"

extern const byte Inv_S_Box[16][16];

byte InvSBox(byte b) {
    return Inv_S_Box[b >> 4][b & 0x0f];
}

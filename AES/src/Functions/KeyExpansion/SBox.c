#include "Types.h"

extern const uint8_t S_Box[16][16];

uint8_t SBox(uint8_t b) {
    return S_Box[b >> 8][b & 0x0f];
}

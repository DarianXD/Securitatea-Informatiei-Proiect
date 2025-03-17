#include "Types.h"

uint8_t SBox(uint8_t b);

word SubWord(word w) {
    uint8_t *bytes = (uint8_t*)&w;
    for (uint8_t i = 0; i < 4; i++) {
        bytes[i] = SBox(bytes[i]);
    }

    return w;
}

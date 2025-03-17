#include "Types.h"

byte SBox(byte b);

word SubWord(word w) {
    byte *bytes = (byte*)&w;
    for (byte i = 0; i < 4; i++) {
        bytes[i] = SBox(bytes[i]);
    }

    return w;
}

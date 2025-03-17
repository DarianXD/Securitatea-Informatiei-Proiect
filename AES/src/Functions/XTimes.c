#include "Types.h"

byte XTimes(byte b) {
    return (byte)(b << 1) ^ ((b & (byte)0x80) ? (byte)0x1b : (byte)0x00);
}

#include "Types.h"

word RotWord(word w) {
    return (w << 8) | (w >> 24);
}

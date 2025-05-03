#include <stdlib.h>
#include "AES.h"
#include "Types.h"

extern const byte Nk_array[];
extern const byte Nr_array[];

extern const word Rcon[];

word SubWord(word w);
word RotWord(word w);

word *KeyExpansion(AES alg, const word *key) {
    /* variables based on selected algorithm */
    byte Nk = Nk_array[alg];
    byte Nr = Nr_array[alg];

    /* return value */
    word *w = malloc((4 * Nr + 4) * sizeof(word));
    if (!w) {
        return NULL;
    }

    byte i = 0;
    while (i < Nk) {
        w[i] = key[i];
        i++;
    }

    while (i <= 4 * Nr + 3) {
        word temp = w[i - 1];
        if (i % Nk == 0) {
            temp = SubWord(RotWord(temp)) ^ Rcon[i / Nk];
        } else if (Nk > 6 && i % Nk == 4) {
            temp = SubWord(temp);
        }
        w[i] = w[i - Nk] ^ temp;
        i++;
    }

    return w;
}

#include "Types.h"

byte GFTimes(byte b, byte c);

void MixColumns(byte val[4][4])
{
    static const byte table[4][4] = {
        {0x02, 0x03, 0x01, 0x01},
        {0x01, 0x02, 0x03, 0x01},
        {0x01, 0x01, 0x02, 0x03},
        {0x03, 0x01, 0x01, 0x02}
    };

    for(byte col = 0; col < 4; ++col)
    {
        byte result[4] = {0};
        for(byte row = 0; row < 4; ++row)
        {
            for(int i = 0; i < 4; ++i)
            {
                result[row] ^= GFTimes(table[row][i], val[i][col]);
            }
        }

        for(int i = 0; i < 4; ++i)
        {
            val[i][col] = result[i];
        }
    }
}

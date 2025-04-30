#include "Types.h"

byte SBox(byte b);

void SubBytes(byte val[4][4])
{
    for(int row = 0; row < 4; ++row)
    {
        for(int col = 0; col < 4; ++col)
        {
            val[row][col] = SBox(val[row][col]);
        }
    }
}

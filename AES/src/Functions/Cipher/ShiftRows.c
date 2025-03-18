#include "Types.h"
#include "string.h"

void ShiftRows(byte val[4][4])
{
    byte valCopy[4][4];
    memcpy(valCopy, val, 16);
    for(int row = 0; row < 4; ++row)
    {
        for(int col = 0; col < 4; ++col)
        {
            val[row][col] = valCopy[row][(row + col) % 4];
        }
    }
}

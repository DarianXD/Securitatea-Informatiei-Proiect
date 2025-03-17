#ifndef TYPES_H
#define TYPES_H

#include <stdint.h>

typedef enum {
    AES_128 = 0,
    AES_192 = 1,
    AES_256 = 2
} AES;

typedef uint32_t word;
typedef uint8_t byte;

#endif /* TYPES_H */

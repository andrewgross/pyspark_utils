from __future__ import annotations

import pyspark.sql.functions as F
from pyspark_utils.helpers import ByteColumn
from pyspark_utils.helpers import chars_to_int
from pyspark_utils.helpers import LongColumn
from pyspark_utils.helpers import StringColumn


def xor_word(
    col1: ByteColumn | StringColumn,
    col2: ByteColumn | StringColumn,
) -> LongColumn:
    """
    Tales two columns references of string data and returns the XOR of the two columns

    Max length of the string is 8 characters (xor as a 64 bit integer)

    Returns an integer representation of the bitwise XOR of the two columns
    """
    return chars_to_int(col1).bitwiseXOR(chars_to_int(col2))


def xor(col1: ByteColumn, col2: ByteColumn, byte_width: int = 64) -> ByteColumn:

    # Use 4 bytes (32 bits) as the word width
    # since we are XORing using 64 bit *signed* integers
    # so we cant use the full width without overflow (NULL in pyspark)
    word_width = 4
    padded_col1 = F.lpad(
        col1,
        byte_width,
        b'\x00',
    )  # Left-pad col1 with '0' up to byte_width
    padded_col2 = F.lpad(
        col2,
        byte_width,
        b'\x00',
    )  # Left-pad col2 with '0' up to byte_width

    chunks = []
    for i in range(0, byte_width, word_width):
        c1_chunk = F.substring(padded_col1, i + 1, word_width)
        c2_chunk = F.substring(padded_col2, i + 1, word_width)

        # XOR the two chunks
        xor_chunk = xor_word(c1_chunk, c2_chunk)

        # Convert XOR result to hexadecimal and pad it
        xor_hex_padded = F.lpad(
            F.hex(xor_chunk),
            2 * word_width,
            '0',
        )  # We want string 0, not byte 0 here because it is hex
        chunks.append(xor_hex_padded)

    return F.to_binary(F.concat(*chunks), F.lit('hex'))

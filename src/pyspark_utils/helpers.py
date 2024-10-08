from __future__ import annotations

from typing import NewType

import pyspark.sql.functions as F
from pyspark.sql import Column

BooleanColumn = NewType('BooleanColumn', Column)
ByteColumn = NewType('ByteColumn', Column)
IntegerColumn = NewType('IntegerColumn', Column)
LongColumn = NewType('LongColumn', Column)
StringColumn = NewType('StringColumn', Column)
HexStringColumn = NewType('HexStringColumn', Column)


def chars_to_int(col: StringColumn) -> LongColumn:
    """
    Take a string, encode it as utf-8, and convert those bytes to a bigint

    Currently blows up if our string is too big
    """
    return F.conv(F.hex(col), 16, 10).cast('bigint')


def pad_key(key: ByteColumn, block_size: int) -> ByteColumn:
    return F.rpad(key, block_size, bytes([0]))


def sha2_binary(col: ByteColumn, num_bits: int) -> ByteColumn:
    return F.to_binary(F.sha2(col, num_bits), F.lit('hex'))

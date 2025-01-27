import logging
import struct

import array

CRC_TABLE = (
    0x00000000, 0xf26b8303, 0xe13b70f7, 0x1350f3f4,
    0xc79a971f, 0x35f1141c, 0x26a1e7e8, 0xd4ca64eb,
    0x8ad958cf, 0x78b2dbcc, 0x6be22838, 0x9989ab3b,
    0x4d43cfd0, 0xbf284cd3, 0xac78bf27, 0x5e133c24,
    0x105ec76f, 0xe235446c, 0xf165b798, 0x030e349b,
    0xd7c45070, 0x25afd373, 0x36ff2087, 0xc494a384,
    0x9a879fa0, 0x68ec1ca3, 0x7bbcef57, 0x89d76c54,
    0x5d1d08bf, 0xaf768bbc, 0xbc267848, 0x4e4dfb4b,
    0x20bd8ede, 0xd2d60ddd, 0xc186fe29, 0x33ed7d2a,
    0xe72719c1, 0x154c9ac2, 0x061c6936, 0xf477ea35,
    0xaa64d611, 0x580f5512, 0x4b5fa6e6, 0xb93425e5,
    0x6dfe410e, 0x9f95c20d, 0x8cc531f9, 0x7eaeb2fa,
    0x30e349b1, 0xc288cab2, 0xd1d83946, 0x23b3ba45,
    0xf779deae, 0x05125dad, 0x1642ae59, 0xe4292d5a,
    0xba3a117e, 0x4851927d, 0x5b016189, 0xa96ae28a,
    0x7da08661, 0x8fcb0562, 0x9c9bf696, 0x6ef07595,
    0x417b1dbc, 0xb3109ebf, 0xa0406d4b, 0x522bee48,
    0x86e18aa3, 0x748a09a0, 0x67dafa54, 0x95b17957,
    0xcba24573, 0x39c9c670, 0x2a993584, 0xd8f2b687,
    0x0c38d26c, 0xfe53516f, 0xed03a29b, 0x1f682198,
    0x5125dad3, 0xa34e59d0, 0xb01eaa24, 0x42752927,
    0x96bf4dcc, 0x64d4cecf, 0x77843d3b, 0x85efbe38,
    0xdbfc821c, 0x2997011f, 0x3ac7f2eb, 0xc8ac71e8,
    0x1c661503, 0xee0d9600, 0xfd5d65f4, 0x0f36e6f7,
    0x61c69362, 0x93ad1061, 0x80fde395, 0x72966096,
    0xa65c047d, 0x5437877e, 0x4767748a, 0xb50cf789,
    0xeb1fcbad, 0x197448ae, 0x0a24bb5a, 0xf84f3859,
    0x2c855cb2, 0xdeeedfb1, 0xcdbe2c45, 0x3fd5af46,
    0x7198540d, 0x83f3d70e, 0x90a324fa, 0x62c8a7f9,
    0xb602c312, 0x44694011, 0x5739b3e5, 0xa55230e6,
    0xfb410cc2, 0x092a8fc1, 0x1a7a7c35, 0xe811ff36,
    0x3cdb9bdd, 0xceb018de, 0xdde0eb2a, 0x2f8b6829,
    0x82f63b78, 0x709db87b, 0x63cd4b8f, 0x91a6c88c,
    0x456cac67, 0xb7072f64, 0xa457dc90, 0x563c5f93,
    0x082f63b7, 0xfa44e0b4, 0xe9141340, 0x1b7f9043,
    0xcfb5f4a8, 0x3dde77ab, 0x2e8e845f, 0xdce5075c,
    0x92a8fc17, 0x60c37f14, 0x73938ce0, 0x81f80fe3,
    0x55326b08, 0xa759e80b, 0xb4091bff, 0x466298fc,
    0x1871a4d8, 0xea1a27db, 0xf94ad42f, 0x0b21572c,
    0xdfeb33c7, 0x2d80b0c4, 0x3ed04330, 0xccbbc033,
    0xa24bb5a6, 0x502036a5, 0x4370c551, 0xb11b4652,
    0x65d122b9, 0x97baa1ba, 0x84ea524e, 0x7681d14d,
    0x2892ed69, 0xdaf96e6a, 0xc9a99d9e, 0x3bc21e9d,
    0xef087a76, 0x1d63f975, 0x0e330a81, 0xfc588982,
    0xb21572c9, 0x407ef1ca, 0x532e023e, 0xa145813d,
    0x758fe5d6, 0x87e466d5, 0x94b49521, 0x66df1622,
    0x38cc2a06, 0xcaa7a905, 0xd9f75af1, 0x2b9cd9f2,
    0xff56bd19, 0x0d3d3e1a, 0x1e6dcdee, 0xec064eed,
    0xc38d26c4, 0x31e6a5c7, 0x22b65633, 0xd0ddd530,
    0x0417b1db, 0xf67c32d8, 0xe52cc12c, 0x1747422f,
    0x49547e0b, 0xbb3ffd08, 0xa86f0efc, 0x5a048dff,
    0x8ecee914, 0x7ca56a17, 0x6ff599e3, 0x9d9e1ae0,
    0xd3d3e1ab, 0x21b862a8, 0x32e8915c, 0xc083125f,
    0x144976b4, 0xe622f5b7, 0xf5720643, 0x07198540,
    0x590ab964, 0xab613a67, 0xb831c993, 0x4a5a4a90,
    0x9e902e7b, 0x6cfbad78, 0x7fab5e8c, 0x8dc0dd8f,
    0xe330a81a, 0x115b2b19, 0x020bd8ed, 0xf0605bee,
    0x24aa3f05, 0xd6c1bc06, 0xc5914ff2, 0x37faccf1,
    0x69e9f0d5, 0x9b8273d6, 0x88d28022, 0x7ab90321,
    0xae7367ca, 0x5c18e4c9, 0x4f48173d, 0xbd23943e,
    0xf36e6f75, 0x0105ec76, 0x12551f82, 0xe03e9c81,
    0x34f4f86a, 0xc69f7b69, 0xd5cf889d, 0x27a40b9e,
    0x79b737ba, 0x8bdcb4b9, 0x988c474d, 0x6ae7c44e,
    0xbe2da0a5, 0x4c4623a6, 0x5f16d052, 0xad7d5351,
)

CRC_INIT = 0

_MASK = 0xFFFFFFFF


def crc_update(crc, data):
    """Update CRC-32C checksum with data.

    Args:
      crc: 32-bit checksum to update as long.
      data: byte array, string or iterable over bytes.
    Returns:
      32-bit updated CRC-32C as long.
    """
    if not isinstance(data, array.array) or data.itemsize != 1:
        buf = array.array("B", data)
    else:
        buf = data

    crc = crc ^ _MASK
    for b in buf:
        table_index = (crc ^ b) & 0xff
        crc = (CRC_TABLE[table_index] ^ (crc >> 8)) & _MASK
    return crc ^ _MASK


def crc_finalize(crc):
    """Finalize CRC-32C checksum.

    This function should be called as last step of crc calculation.
    Args:
      crc: 32-bit checksum as long.
    Returns:
      finalized 32-bit checksum as long
    """
    return crc & _MASK


def crc(data):
    """Compute CRC-32C checksum of the data.

    Args:
      data: byte array, string or iterable over bytes.
    Returns:
      32-bit CRC-32C checksum of data as long.
    """
    return crc_finalize(crc_update(CRC_INIT, data))


BLOCK_SIZE = 32 * 1024

HEADER_FORMAT = '<IHB'

HEADER_LENGTH = struct.calcsize(HEADER_FORMAT)

RECORD_TYPE_NONE = 0

RECORD_TYPE_FULL = 1

RECORD_TYPE_FIRST = 2

RECORD_TYPE_MIDDLE = 3

RECORD_TYPE_LAST = 4


class Error(Exception):
    """Base class for exceptions in this module."""


class InvalidRecordError(Error):
    """Raised when invalid record encountered."""


class FileReader(object):
    """Interface specification for writers to be used with recordrecords module.

    FileReader defines a reader with position and efficient seek/position
    determining. All reads occur at current position.
    """

    def read(self, size):
        """Read data from file.

        Reads data from current position and advances position past the read data
        block.
        Args:
          size: number of bytes to read.
        Returns:
          iterable over bytes. If number of bytes read is less then 'size' argument,
          it is assumed that end of file was reached.
        """
        raise NotImplementedError()

    def tell(self):
        """Get current file position.

        Returns:
          current position as a byte offset in the file as integer.
        """
        raise NotImplementedError()


_CRC_MASK_DELTA = 0xa282ead8


def _mask_crc(crc):
    """Mask crc.

    Args:
      crc: integer crc.
    Returns:
      masked integer crc.
    """
    return (((crc >> 15) | (crc << 17)) + _CRC_MASK_DELTA) & 0xFFFFFFFF


def _unmask_crc(masked_crc):
    """Unmask crc.

    Args:
      masked_crc: masked integer crc.
    Retruns:
      orignal crc.
    """
    rot = (masked_crc - _CRC_MASK_DELTA) & 0xFFFFFFFF
    return ((rot >> 17) | (rot << 15)) & 0xFFFFFFFF


class RecordsReader(object):
    """A reader for records format."""

    def __init__(self, reader):
        self.__reader = reader

    def __try_read_record(self):
        """Try reading a record.

        Returns:
          (data, record_type) tuple.
        Raises:
          EOFError: when end of file was reached.
          InvalidRecordError: when valid record could not be read.
        """
        block_remaining = BLOCK_SIZE - self.__reader.tell() % BLOCK_SIZE
        if block_remaining < HEADER_LENGTH:
            return ('', RECORD_TYPE_NONE)

        header = self.__reader.read(HEADER_LENGTH)
        if len(header) != HEADER_LENGTH:
            raise EOFError('Read %s bytes instead of %s' %
                           (len(header), HEADER_LENGTH))

        (masked_crc, length, record_type) = struct.unpack(HEADER_FORMAT, header)
        crc = _unmask_crc(masked_crc)

        if length + HEADER_LENGTH > block_remaining:
            raise InvalidRecordError('Length is too big')

        data = self.__reader.read(length)
        if len(data) != length:
            raise EOFError('Not enough data read. Expected: %s but got %s' %
                           (length, len(data)))

        if record_type == RECORD_TYPE_NONE:
            return ('', record_type)

        actual_crc = crc_update(CRC_INIT, [record_type])
        actual_crc = crc_update(actual_crc, data)
        actual_crc = crc_finalize(actual_crc)

        if actual_crc != crc:
            raise InvalidRecordError('Data crc does not match')
        return (data, record_type)

    def __sync(self):
        """Skip reader to the block boundary."""
        pad_length = BLOCK_SIZE - self.__reader.tell() % BLOCK_SIZE
        if pad_length and pad_length != BLOCK_SIZE:
            data = self.__reader.read(pad_length)
            if len(data) != pad_length:
                raise EOFError('Read %d bytes instead of %d' %
                               (len(data), pad_length))

    def read(self):
        """Reads record from current position in reader."""
        data = None
        while True:
            last_offset = self.tell()
            try:
                (chunk, record_type) = self.__try_read_record()
                if record_type == RECORD_TYPE_NONE:
                    self.__sync()
                elif record_type == RECORD_TYPE_FULL:
                    if data is not None:
                        logging.warning(
                            "Ordering corruption: Got FULL record while already "
                            "in a chunk at offset %d", last_offset)
                    return chunk
                elif record_type == RECORD_TYPE_FIRST:
                    if data is not None:
                        logging.warning(
                            "Ordering corruption: Got FIRST record while already "
                            "in a chunk at offset %d", last_offset)
                    data = chunk
                elif record_type == RECORD_TYPE_MIDDLE:
                    if data is None:
                        logging.warning(
                            "Ordering corruption: Got MIDDLE record before FIRST "
                            "record at offset %d", last_offset)
                    else:
                        data += chunk
                elif record_type == RECORD_TYPE_LAST:
                    if data is None:
                        logging.warning(
                            "Ordering corruption: Got LAST record but no chunk is in "
                            "progress at offset %d", last_offset)
                    else:
                        result = data + chunk
                        data = None
                        return result
                else:
                    raise InvalidRecordError("Unsupported record type: %s" % record_type)

            except InvalidRecordError:
                logging.warning("Invalid record encountered at %s. Syncing to "
                                "the next block", last_offset)
                data = None
                self.__sync()

    def __iter__(self):
        """Iterate through records."""
        try:
            while True:
                yield self.read()
        except EOFError:
            pass

    def tell(self):
        """Return file's current position."""
        return self.__reader.tell()
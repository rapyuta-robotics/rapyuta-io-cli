import enum


class DiskCapacity(int, enum.Enum):
    """
    Enumeration variables for disk capacity. The type may be one of the following \n
    DiskCapacity.GiB_4 \n
    DiskCapacity.GiB_8 \n
    DiskCapacity.GiB_16 \n
    DiskCapacity.GiB_32 \n
    DiskCapacity.GiB_64 \n
    DiskCapacity.GiB_128 \n
    DiskCapacity.GiB_256 \n
    DiskCapacity.GiB_512 \n
    """

    def __str__(self):
        return str(self.value)

    GiB_4 = 4
    GiB_8 = 8
    GiB_16 = 16
    GiB_32 = 32
    GiB_64 = 64
    GiB_128 = 128
    GiB_256 = 256
    GiB_512 = 512

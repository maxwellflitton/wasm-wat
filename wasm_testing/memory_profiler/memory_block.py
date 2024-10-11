"""
Defines a memory block with headers and data.
"""
from typing import List, Optional


class MemoryBlock:
    """
    A block of memory in the page

    Attributes:
        ptr: a pointer to where the memory block is in the page
        free: a boolean indicating if the memory block is free
        next_free_ptr: a pointer to the next free memory block
        size: the size of the data section of the memory block
        data: the data section of the memory block
    """
    def __init__(self, memory: List[int], ptr: int) -> None:
        """
        The constructor for the MemoryBlock.

        :param memory: A segment of memory to be processed
                       (must be exact, please use self.from_raw_block if not exact)
        :param ptr: a pointer to where the memory block is in the page
        """
        self.ptr: int = ptr
        self.free: bool = self.check_free(memory=memory)
        self.next_free_ptr: Optional[int] = self.extract_next_free(memory=memory)
        self.size: int = self.extract_size(memory=memory)
        self.data: List[int] = self.extract_data(size=self.size, memory=memory)

    @staticmethod
    def from_raw_block(raw_memory: List[int], ptr: int) -> "MemoryBlock":
        """
        Extracts the memory block from an unprocessed page.

        :param raw_memory: the entire page of memory
        :param ptr: a pointer to where the memory block is in the page
        :return: a constructed memory block to be profiled or compared against
        """
        size = MemoryBlock.extract_size_from_raw(raw_memory=raw_memory, ptr=ptr)
        mem_slice = raw_memory[ptr: ptr + size + 12]
        return MemoryBlock(memory=mem_slice, ptr=ptr)

    @staticmethod
    def extract_size_from_raw(raw_memory: List[int], ptr: int) -> int:
        """
        Gets the size of the data section of the memory block from a page of memory.

        :param raw_memory: the entire page of memory unprocessed
        :param ptr: a pointer to where the memory block is in the page
        :return: the size of the data for the memory block
        """
        return MemoryBlock.extract_unsigned_integer(data=raw_memory[ptr + 8: ptr + 12])

    @staticmethod
    def check_free(memory: List[int]) -> bool:
        """
        Checks if the memory block is free.

        :param memory: the memory block to check
        :return: a boolean indicating if the memory block is free
        """
        integer_value = MemoryBlock.extract_unsigned_integer(memory[0:4])
        if integer_value == 0:
            return True
        return False

    @staticmethod
    def extract_next_free(memory: List[int]) -> Optional[int]:
        pointer = MemoryBlock.extract_unsigned_integer(memory[4:8])
        if pointer == -1:
            return None
        return pointer

    @staticmethod
    def extract_size(memory: List[int]) -> int:
        return MemoryBlock.extract_unsigned_integer(memory[8:12])

    @staticmethod
    def extract_data(size: int, memory: List[int]) -> List[int]:
        return memory[12: 12 + size]

    @staticmethod
    def extract_unsigned_integer(data: List[int]) -> int:
        byte_data = bytes(data)
        unsigned_value = int.from_bytes(byte_data, byteorder='little', signed=False)
        if unsigned_value >= 2 ** 31:
            signed_value = unsigned_value - 2 ** 32
        else:
            signed_value = unsigned_value
        return signed_value


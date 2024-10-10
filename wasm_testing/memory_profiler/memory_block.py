from typing import List, Optional


class MemoryBlock:

    def __init__(self, memory: List[int], ptr: int) -> None:
        self.ptr: int = ptr
        self.free: bool = self.check_free(memory=memory)
        self.next_free_ptr: Optional[int] = self.extract_next_free(memory=memory)
        self.size: int = self.extract_size(memory=memory)
        self.data: List[int] = self.extract_data(size=self.size, memory=memory)

    # TODO => implement the self.ptr, free, next, and size getters as byte arrays

    @staticmethod
    def check_free(memory: List[int]) -> bool:
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


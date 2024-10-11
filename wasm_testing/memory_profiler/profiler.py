from typing import List

from wasm_testing.memory_profiler.memory_block import MemoryBlock


class MemoryProfiler:
    """
    The MemoryProfiler class is used to process an entire page of memory and extract the memory blocks from.

    Attributes:
        raw_memory: the entire page of memory to be processed
        memory_blocks: a list of memory blocks extracted from the raw memory
    """
    def __init__(self, raw_memory: List[int]) -> None:
        """
        The constructor for the MemoryProfiler.

        :param raw_memory: the entire page of memory to be processed
        """
        self.raw_memory: List[int] = raw_memory
        self.memory_blocks: List[MemoryBlock] = MemoryProfiler.extract_memory_blocks(raw_memory=raw_memory)

    @staticmethod
    def extract_memory_blocks(raw_memory: List[int]) -> List[MemoryBlock]:
        """
        Convert the raw memory into a list of memory blocks.

        :param raw_memory: the entire page of memory to be processed
        :return: a list of memory blocks
        """
        ptr = 0
        memory_blocks = []
        while ptr < len(raw_memory):
            if len(raw_memory[ptr:]) < 12:
                break
            check = raw_memory[ptr: ptr + 12]
            if sum(check) == 0:
                break
            size = MemoryBlock.extract_size_from_raw(raw_memory, ptr)
            memory_blocks.append(MemoryBlock.from_raw_block(raw_memory, ptr))
            ptr += size
            ptr += 12
        return memory_blocks

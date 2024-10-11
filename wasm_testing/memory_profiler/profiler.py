from wasm_testing.memory_profiler.memory_block import MemoryBlock
from typing import List


class MemoryProfiler:

    def __init__(self, raw_memory: List[int]) -> None:
        self.raw_memory: List[int] = raw_memory
        self.memory_blocks: List[MemoryBlock] = []

    @staticmethod
    def extract_memory_blocks():
        pass

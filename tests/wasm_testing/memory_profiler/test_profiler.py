from typing import List
from unittest import TestCase, main

from tests.test_utils.raw_mem_data import RawMemBlockData
from wasm_testing.memory_profiler.memory_block import MemoryBlock
from wasm_testing.memory_profiler.profiler import MemoryProfiler


class TestMemoryProfiler(TestCase):

    def setUp(self):
        self.data = RawMemBlockData()

    def tearDown(self):
        pass

    def compare_mem_blocks(self, data: List[int], ptr: int, block2: MemoryBlock):
        block1 = MemoryBlock(memory=data, ptr=ptr)
        self.assertEqual(block1.ptr, block2.ptr)
        self.assertEqual(block1.free, block2.free)
        self.assertEqual(block1.next_free_ptr, block2.next_free_ptr)
        self.assertEqual(block1.size, block2.size)
        self.assertEqual(block1.data, block2.data)

    def test___init__(self):
        raw_data = self.data.total + [0, 0, 0, 0, 0]
        profiler = MemoryProfiler(raw_memory=raw_data)

        self.assertEqual(9, len(profiler.memory_blocks))

        self.compare_mem_blocks(data=self.data.one, ptr=self.data.one_ptr, block2=profiler.memory_blocks[0])
        self.compare_mem_blocks(data=self.data.two, ptr=self.data.two_ptr, block2=profiler.memory_blocks[1])
        self.compare_mem_blocks(data=self.data.three, ptr=self.data.three_ptr, block2=profiler.memory_blocks[2])
        self.compare_mem_blocks(data=self.data.four, ptr=self.data.four_ptr, block2=profiler.memory_blocks[3])
        self.compare_mem_blocks(data=self.data.five, ptr=self.data.five_ptr, block2=profiler.memory_blocks[4])
        self.compare_mem_blocks(data=self.data.six, ptr=self.data.six_ptr, block2=profiler.memory_blocks[5])
        self.compare_mem_blocks(data=self.data.seven, ptr=self.data.seven_ptr, block2=profiler.memory_blocks[6])
        self.compare_mem_blocks(data=self.data.eight, ptr=self.data.eight_ptr, block2=profiler.memory_blocks[7])
        self.compare_mem_blocks(data=self.data.nine, ptr=self.data.nine_ptr, block2=profiler.memory_blocks[8])


if __name__ == '__main__':
    main()

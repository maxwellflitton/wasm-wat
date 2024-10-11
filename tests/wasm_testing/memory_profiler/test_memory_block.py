from unittest import TestCase, main

from tests.test_utils.raw_mem_data import RawMemBlockData
from wasm_testing.memory_profiler.memory_block import MemoryBlock


class TestMemoryBlock(TestCase):

    def setUp(self):
        self.data = RawMemBlockData()
        self.one = MemoryBlock(memory=self.data.one, ptr=self.data.one_ptr)
        self.two = MemoryBlock(memory=self.data.two, ptr=self.data.two_ptr)
        self.three = MemoryBlock(memory=self.data.three, ptr=self.data.three_ptr)
        self.four = MemoryBlock(memory=self.data.four, ptr=self.data.four_ptr)
        self.five = MemoryBlock(memory=self.data.five, ptr=self.data.five_ptr)
        self.six = MemoryBlock(memory=self.data.six, ptr=self.data.six_ptr)
        self.seven = MemoryBlock(memory=self.data.seven, ptr=self.data.seven_ptr)
        self.eight = MemoryBlock(memory=self.data.eight, ptr=self.data.eight_ptr)
        self.nine = MemoryBlock(memory=self.data.nine, ptr=self.data.nine_ptr)

    def tearDown(self):
        pass

    def assert_mem_block_from_raw(self, ptr: int, compare_block: MemoryBlock):
        new_block = MemoryBlock.from_raw_block(raw_memory=self.data.total, ptr=ptr)
        self.assertEqual(new_block.size, compare_block.size)
        self.assertEqual(new_block.next_free_ptr, compare_block.next_free_ptr)
        self.assertEqual(new_block.data, compare_block.data)
        self.assertEqual(new_block.free, compare_block.free)
        self.assertEqual(new_block.ptr, compare_block.ptr)

    def test_test___init__(self):
        self.assertEqual(True, self.one.free)
        self.assertEqual(None, self.one.next_free_ptr)
        self.assertEqual(20, self.one.size)

        self.assertEqual(True, self.two.free)
        self.assertEqual(69, self.two.next_free_ptr)
        self.assertEqual(5, self.two.size)

        self.assertEqual(False, self.three.free)
        self.assertEqual(None, self.three.next_free_ptr)
        self.assertEqual(20, self.three.size)

        self.assertEqual(True, self.four.free)
        self.assertEqual(97, self.four.next_free_ptr)
        self.assertEqual(20, self.four.size)

        self.assertEqual(True, self.five.free)
        self.assertEqual(136, self.five.next_free_ptr)
        self.assertEqual(3, self.five.size)

        self.assertEqual(False, self.six.free)
        self.assertEqual(None, self.six.next_free_ptr)
        self.assertEqual(20, self.six.size)

        self.assertEqual(True, self.seven.free)
        self.assertEqual(180, self.seven.next_free_ptr)
        self.assertEqual(8, self.seven.size)

        self.assertEqual(False, self.eight.free)
        self.assertEqual(None, self.eight.next_free_ptr)
        self.assertEqual(20, self.eight.size)

        self.assertEqual(True, self.nine.free)
        self.assertEqual(0, self.nine.next_free_ptr)
        self.assertEqual(20, self.nine.size)

    def test_extract_size_from_raw(self):
        self.assertEqual(20, MemoryBlock.extract_size_from_raw(raw_memory=self.data.total, ptr=self.data.one_ptr))
        self.assertEqual(5, MemoryBlock.extract_size_from_raw(raw_memory=self.data.total, ptr=self.data.two_ptr))
        self.assertEqual(20, MemoryBlock.extract_size_from_raw(raw_memory=self.data.total, ptr=self.data.three_ptr))
        self.assertEqual(20, MemoryBlock.extract_size_from_raw(raw_memory=self.data.total, ptr=self.data.four_ptr))

        self.assertEqual(3, MemoryBlock.extract_size_from_raw(raw_memory=self.data.total, ptr=self.data.five_ptr))

        self.assertEqual(20, MemoryBlock.extract_size_from_raw(raw_memory=self.data.total, ptr=self.data.six_ptr))
        self.assertEqual(8, MemoryBlock.extract_size_from_raw(raw_memory=self.data.total, ptr=self.data.seven_ptr))
        self.assertEqual(20, MemoryBlock.extract_size_from_raw(raw_memory=self.data.total, ptr=self.data.eight_ptr))
        self.assertEqual(20, MemoryBlock.extract_size_from_raw(raw_memory=self.data.total, ptr=self.data.nine_ptr))

    def test_from_raw_block(self):
        self.assert_mem_block_from_raw(ptr=self.data.one_ptr, compare_block=self.one)
        self.assert_mem_block_from_raw(ptr=self.data.two_ptr, compare_block=self.two)
        self.assert_mem_block_from_raw(ptr=self.data.three_ptr, compare_block=self.three)
        self.assert_mem_block_from_raw(ptr=self.data.four_ptr, compare_block=self.four)
        self.assert_mem_block_from_raw(ptr=self.data.five_ptr, compare_block=self.five)
        self.assert_mem_block_from_raw(ptr=self.data.six_ptr, compare_block=self.six)
        self.assert_mem_block_from_raw(ptr=self.data.seven_ptr, compare_block=self.seven)
        self.assert_mem_block_from_raw(ptr=self.data.eight_ptr, compare_block=self.eight)
        self.assert_mem_block_from_raw(ptr=self.data.nine_ptr, compare_block=self.nine)


if __name__ == '__main__':
    main()

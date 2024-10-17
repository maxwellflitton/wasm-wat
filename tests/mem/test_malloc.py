import os
from unittest import TestCase, main

from wasmtime import Store, Module, Instance

from wasm_testing.memory_profiler.memory_block import MemoryBlock
from wasm_testing.memory_profiler.profiler import MemoryProfiler


class TestAdd(TestCase):

    def setUp(self):
        self.file_path = os.path.dirname(os.path.abspath(__file__))
        self.base_path = os.path.dirname(os.path.dirname(self.file_path))
        build_path = os.path.join(self.base_path, 'build')
        build_path = os.path.join(build_path, 'mem')
        self.module_path = os.path.join(build_path, 'malloc.wasm')
        self.store = Store()
        self.module = Module.from_file(self.store.engine, self.module_path)
        self.instance = Instance(self.store, self.module, [])

    def compare_mem_blocks(self, mem_block: MemoryBlock, expected_data: list) -> None:
        self.assertEqual(mem_block.ptr, expected_data[0])
        self.assertEqual(mem_block.free, expected_data[1])
        self.assertEqual(mem_block.size, expected_data[2])
        self.assertEqual(mem_block.next_free_ptr, expected_data[3])
        self.assertEqual(mem_block.data, expected_data[4])

    def profile_entire_memory(self, expected_mem: list) -> None:
        memory = self.instance.exports(self.store)["malloc_memory"]
        mem_profiler = MemoryProfiler(raw_memory=memory.data_ptr(self.store)[0:64000])

        for i in range(0, len(expected_mem)):
            self.compare_mem_blocks(
                mem_block=mem_profiler.memory_blocks[i],
                expected_data=expected_mem[i]
            )

    def test_basic_malloc(self):
        malloc = self.instance.exports(self.store)["mem_malloc_malloc"]
        outcome = malloc(self.store, 20)
        self.assertEqual(0, outcome)

        # Access the exported memory
        memory = self.instance.exports(self.store)["malloc_memory"]
        mem_profiler = MemoryProfiler(raw_memory=memory.data_ptr(self.store)[0:64000])

        # Inspect the memory
        self.assertEqual(1, len(mem_profiler.memory_blocks))

        self.compare_mem_blocks(
            mem_block=mem_profiler.memory_blocks[0],
            expected_data=[0, False, 20, None, [0] * 20]
        )

        is_mem_free = self.instance.exports(self.store)["mem_malloc_is_mem_free"]
        is_mem_free = is_mem_free(self.store, 0)
        self.assertEqual(1, is_mem_free)

        get_next_free_mem = self.instance.exports(self.store)["mem_malloc_get_next_free_mem"]
        get_next_free_mem = get_next_free_mem(self.store, 0)
        self.assertEqual(-1, get_next_free_mem)

        get_mem_length = self.instance.exports(self.store)["mem_malloc_get_mem_length"]
        get_mem_length = get_mem_length(self.store, 0)
        self.assertEqual(20, get_mem_length)

        outcome = malloc(self.store, 5)
        self.assertEqual(32, outcome)

        # Access the exported memory
        memory = self.instance.exports(self.store)["malloc_memory"]
        mem_profiler = MemoryProfiler(raw_memory=memory.data_ptr(self.store)[0:64000])

        # Inspect the memory
        self.assertEqual(2, len(mem_profiler.memory_blocks))

        # assert that the first block is still the same
        self.compare_mem_blocks(
            mem_block=mem_profiler.memory_blocks[0],
            expected_data=[0, False, 20, None, [0] * 20]
        )
        self.compare_mem_blocks(
            mem_block=mem_profiler.memory_blocks[1],
            expected_data=[32, False, 5, None, [0] * 5]
        )

    def test_basic_free(self):
        malloc = self.instance.exports(self.store)["mem_malloc_malloc"]
        one = malloc(self.store, 20)
        two = malloc(self.store, 5)
        three = malloc(self.store, 8)
        four = malloc(self.store, 12)
        five = malloc(self.store, 8)
        six = malloc(self.store, 15)
        seven = malloc(self.store, 7)
        eight = malloc(self.store, 3)

        self.assertEqual(0, one)
        self.assertEqual(0 + 12 + 20, two)
        self.assertEqual(two + 12 + 5, three)
        self.assertEqual(three + 12 + 8, four)
        self.assertEqual(four + 12 + 12, five)
        self.assertEqual(five + 12 + 8, six)
        self.assertEqual(six + 12 + 15, seven)
        self.assertEqual(seven + 12 + 7, eight)

        expected_mem = [
            [0, False, 20, None, [0] * 20],
            [32, False, 5, None, [0] * 5],
            [49, False, 8, None, [0] * 8],
            [69, False, 12, None, [0] * 12],
            [93, False, 8, None, [0] * 8],
            [113, False, 15, None, [0] * 15],
            [140, False, 7, None, [0] * 7],
            [159, False, 3, None, [0] * 3]
        ]
        self.profile_entire_memory(expected_mem=expected_mem)

        # start freeing memory
        free_func = self.instance.exports(self.store)["mem_malloc_free"]

        free_func(self.store, two)
        expected_mem = [
            [0, False, 20, None, [0] * 20],
            [32, True, 5, None, [0] * 5],
            [49, False, 8, None, [0] * 8],
            [69, False, 12, None, [0] * 12],
            [93, False, 8, None, [0] * 8],
            [113, False, 15, None, [0] * 15],
            [140, False, 7, None, [0] * 7],
            [159, False, 3, None, [0] * 3]
        ]
        self.profile_entire_memory(expected_mem=expected_mem)

        free_func(self.store, four)
        expected_mem = [
            [0, False, 20, None, [0] * 20],
            [32, True, 5, 69, [0] * 5],
            [49, False, 8, None, [0] * 8],
            [69, True, 12, None, [0] * 12],
            [93, False, 8, None, [0] * 8],
            [113, False, 15, None, [0] * 15],
            [140, False, 7, None, [0] * 7],
            [159, False, 3, None, [0] * 3]
        ]
        self.profile_entire_memory(expected_mem=expected_mem)

        free_func(self.store, seven)
        expected_mem = [
            [0, False, 20, None, [0] * 20],
            [32, True, 5, 69, [0] * 5],
            [49, False, 8, None, [0] * 8],
            [69, True, 12, 140, [0] * 12],
            [93, False, 8, None, [0] * 8],
            [113, False, 15, None, [0] * 15],
            [140, True, 7, None, [0] * 7],
            [159, False, 3, None, [0] * 3]
        ]
        self.profile_entire_memory(expected_mem=expected_mem)

        free_func(self.store, eight)
        expected_mem = [
            [0, False, 20, None, [0] * 20],
            [32, True, 5, 69, [0] * 5],
            [49, False, 8, None, [0] * 8],
            [69, True, 12, 140, [0] * 12],
            [93, False, 8, None, [0] * 8],
            [113, False, 15, None, [0] * 15],
            [140, True, 7, 159, [0] * 7],
            [159, True, 3, None, [0] * 3]
        ]
        self.profile_entire_memory(expected_mem=expected_mem)

    def test_malloc_existing(self):
        # define a range of memory allocations
        malloc = self.instance.exports(self.store)["mem_malloc_malloc"]
        one = malloc(self.store, 20)
        two = malloc(self.store, 5)
        three = malloc(self.store, 20)
        four = malloc(self.store, 20)
        five = malloc(self.store, 3)
        six = malloc(self.store, 20)
        seven = malloc(self.store, 8)
        eight = malloc(self.store, 20)
        nine = malloc(self.store, 20)

        expected_mem = [
            [0, False, 20, None, [0] * 20],
            [32, False, 5, None, [0] * 5],
            [49, False, 20, None, [0] * 20],
            [81, False, 20, None, [0] * 20],
            [113, False, 3, None, [0] * 3],
            [128, False, 20, None, [0] * 20],
            [160, False, 8, None, [0] * 8],
            [180, False, 20, None, [0] * 20],
            [212, False, 20, None, [0] * 20]
        ]
        self.profile_entire_memory(expected_mem=expected_mem)

        # free some memory up
        free_func = self.instance.exports(self.store)["mem_malloc_free"]
        free_func(self.store, two)
        free_func(self.store, four)
        free_func(self.store, five)
        free_func(self.store, seven)
        free_func(self.store, nine)
        free_func(self.store, one)

        expected_mem = [
            [0, True, 20, None, [0] * 20],
            [32, True, 5, 81, [0] * 5],
            [49, False, 20, None, [0] * 20],
            [81, True, 20, 113, [0] * 20],
            [113, True, 3, 160, [0] * 3],
            [128, False, 20, None, [0] * 20],
            [160, True, 8, 212, [0] * 8],
            [180, False, 20, None, [0] * 20],
            [212, True, 20, 0, [0] * 20]
        ]
        self.profile_entire_memory(expected_mem=expected_mem)

        get_first_freed = self.instance.exports(self.store)["mem_malloc_get_first_freed"]
        first_freed = get_first_freed(self.store)
        self.assertEqual(32, first_freed)

        # get the first realloc
        outcome = malloc(self.store, 4)
        self.assertEqual(32, outcome)

        expected_mem = [
            [0, True, 20, None, [0] * 20],
            [32, False, 5, None, [0] * 5],      # This block is now free thus the next free pointer is None
            [49, False, 20, None, [0] * 20],
            [81, True, 20, 113, [0] * 20],
            [113, True, 3, 160, [0] * 3],
            [128, False, 20, None, [0] * 20],
            [160, True, 8, 212, [0] * 8],
            [180, False, 20, None, [0] * 20],
            [212, True, 20, 0, [0] * 20]
        ]
        self.profile_entire_memory(expected_mem=expected_mem)
        first_freed = get_first_freed(self.store)
        self.assertEqual(81, first_freed)

        # call the next first realloc
        outcome = malloc(self.store, 20)
        self.assertEqual(81, outcome)

        expected_mem = [
            [0, True, 20, None, [0] * 20],
            [32, False, 5, None, [0] * 5],
            [49, False, 20, None, [0] * 20],
            [81, False, 20, None, [0] * 20],
            [113, True, 3, 160, [0] * 3],
            [128, False, 20, None, [0] * 20],
            [160, True, 8, 212, [0] * 8],
            [180, False, 20, None, [0] * 20],
            [212, True, 20, 0, [0] * 20]
        ]
        self.profile_entire_memory(expected_mem=expected_mem)
        first_freed = get_first_freed(self.store)
        self.assertEqual(113, first_freed)

    def test_scan_and_stitching(self):
        malloc = self.instance.exports(self.store)["mem_malloc_malloc"]
        one = malloc(self.store, 20)
        two = malloc(self.store, 5)
        three = malloc(self.store, 8)
        four = malloc(self.store, 12)
        five = malloc(self.store, 8)
        six = malloc(self.store, 15)
        seven = malloc(self.store, 7)
        eight = malloc(self.store, 3)
        nine = malloc(self.store, 20)
        ten = malloc(self.store, 5)

        expected_mem = [
            [0, False, 20, None, [0] * 20],
            [32, False, 5, None, [0] * 5],
            [49, False, 8, None, [0] * 8],
            [69, False, 12, None, [0] * 12],
            [93, False, 8, None, [0] * 8],
            [113, False, 15, None, [0] * 15],
            [140, False, 7, None, [0] * 7],
            [159, False, 3, None, [0] * 3],
            [174, False, 20, None, [0] * 20],
            [206, False, 5, None, [0] * 5]
        ]
        self.profile_entire_memory(expected_mem=expected_mem)

        # free some memory up
        free_func = self.instance.exports(self.store)["mem_malloc_free"]
        free_func(self.store, two)
        free_func(self.store, four)
        free_func(self.store, five)
        free_func(self.store, seven)
        free_func(self.store, nine)
        free_func(self.store, one)

        expected_mem = [
            [0, True, 20, None, [0] * 20],
            [32, True, 5, 69, [0] * 5],
            [49, False, 8, None, [0] * 8],
            [69, True, 12, 93, [0] * 12],
            [93, True, 8, 140, [0] * 8],
            [113, False, 15, None, [0] * 15],
            [140, True, 7, 174, [0] * 7],
            [159, False, 3, None, [0] * 3],
            [174, True, 20, 0, [0] * 20],
            [206, False, 5, None, [0] * 5]
        ]
        self.profile_entire_memory(expected_mem=expected_mem)

        get_first_freed = self.instance.exports(self.store)["mem_malloc_get_first_freed"]
        first_freed = get_first_freed(self.store)
        self.assertEqual(32, first_freed)

        # we now have to scan for memory blocks that are free and stitch them together
        outcome = malloc(self.store, 15)
        self.assertEqual(174, outcome)

        expected_mem = [
            [0, True, 20, None, [0] * 20],
            [32, True, 5, 69, [0] * 5],
            [49, False, 8, None, [0] * 8],
            [69, True, 12, 93, [0] * 12],
            [93, True, 8, 140, [0] * 8],
            [113, False, 15, None, [0] * 15],
            [140, True, 7, 0, [0] * 7],
            [159, False, 3, None, [0] * 3],
            [174, False, 20, None, [0] * 20],
            [206, False, 5, None, [0] * 5]
        ]
        self.profile_entire_memory(expected_mem=expected_mem)

        # Assert that if the size is too big for anything a new block is created
        outcome = malloc(self.store, 30)
        self.assertEqual(223, outcome)

        expected_mem = [
            [0, True, 20, None, [0] * 20],
            [32, True, 5, 69, [0] * 5],
            [49, False, 8, None, [0] * 8],
            [69, True, 12, 93, [0] * 12],
            [93, True, 8, 140, [0] * 8],
            [113, False, 15, None, [0] * 15],
            [140, True, 7, 0, [0] * 7],
            [159, False, 3, None, [0] * 3],
            [174, False, 20, None, [0] * 20],
            [206, False, 5, None, [0] * 5],
            [223, False, 30, None, [0] * 30]
        ]
        self.profile_entire_memory(expected_mem=expected_mem)


if __name__ == '__main__':
    main()

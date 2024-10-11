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

    def test_basic_malloc(self):
        malloc = self.instance.exports(self.store)["malloc"]
        outcome = malloc(self.store, 20)
        self.assertEqual(0, outcome)

        # Access the exported memory
        memory = self.instance.exports(self.store)["malloc_memory"]
        mem_profiler = MemoryProfiler(raw_memory=memory.data_ptr(self.store)[0:64000])

        # Inspect the memory
        self.assertEqual(1, len(mem_profiler.memory_blocks))

        self.assertEqual(0, mem_profiler.memory_blocks[0].ptr)
        self.assertEqual(False, mem_profiler.memory_blocks[0].free)
        self.assertEqual(20, mem_profiler.memory_blocks[0].size)
        self.assertEqual(None, mem_profiler.memory_blocks[0].next_free_ptr)
        self.assertEqual([0] * 20, mem_profiler.memory_blocks[0].data)

        is_mem_free = self.instance.exports(self.store)["is_mem_free"]
        is_mem_free = is_mem_free(self.store, 0)
        self.assertEqual(1, is_mem_free)

        get_next_free_mem = self.instance.exports(self.store)["get_next_free_mem"]
        get_next_free_mem = get_next_free_mem(self.store, 0)
        self.assertEqual(-1, get_next_free_mem)

        get_mem_length = self.instance.exports(self.store)["get_mem_length"]
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
        self.assertEqual(0, mem_profiler.memory_blocks[0].ptr)
        self.assertEqual(False, mem_profiler.memory_blocks[0].free)
        self.assertEqual(20, mem_profiler.memory_blocks[0].size)
        self.assertEqual(None, mem_profiler.memory_blocks[0].next_free_ptr)
        self.assertEqual([0] * 20, mem_profiler.memory_blocks[0].data)

        # assert that the second block is as expected
        self.assertEqual(32, mem_profiler.memory_blocks[1].ptr)
        self.assertEqual(False, mem_profiler.memory_blocks[1].free)
        self.assertEqual(5, mem_profiler.memory_blocks[1].size)
        self.assertEqual(None, mem_profiler.memory_blocks[1].next_free_ptr)
        self.assertEqual([0] * 5, mem_profiler.memory_blocks[1].data)

    def test_basic_free(self):
        malloc = self.instance.exports(self.store)["malloc"]
        one = malloc(self.store, 20)
        two = malloc(self.store, 20)
        three = malloc(self.store, 20)
        four = malloc(self.store, 20)
        five = malloc(self.store, 20)
        six = malloc(self.store, 20)
        seven = malloc(self.store, 20)
        eight = malloc(self.store, 20)

        self.print_mem()

        self.assertEqual(28, two)
        self.assertEqual(84, four)
        self.assertEqual(168, seven)
        self.assertEqual(196, eight)

        free_func = self.instance.exports(self.store)["free"]
        free_func(self.store, two)
        self.print_mem()

        free_func(self.store, four)
        self.print_mem()

        free_func(self.store, seven)
        self.print_mem()

        free_func(self.store, eight)
        mem_grid = self.get_mem_grid()
        expected_grid = [
            [1, 0, 0, 0, 255, 255, 255, 255, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 84, 0, 0, 0, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 255, 255, 255, 255, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 168, 0, 0, 0, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 255, 255, 255, 255, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 255, 255, 255, 255, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 196, 0, 0, 0, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 255, 255, 255, 255, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]
        self.assertEqual(
            expected_grid,
            mem_grid
        )

    def test_malloc_existing(self):
        # define a range of memory allocations
        malloc = self.instance.exports(self.store)["malloc"]
        one = malloc(self.store, 20)  # 0 => 28 => 20
        two = malloc(self.store, 5)  # 28 => 41 => 5
        three = malloc(self.store, 20)  # 41 => 69 => 20
        four = malloc(self.store, 20)  # 69 => 97 => 20
        five = malloc(self.store, 3)  # 97 => 108 => 3
        six = malloc(self.store, 20)  # 108 => 136 => 20
        seven = malloc(self.store, 8)  # 136 => 152 => 8
        eight = malloc(self.store, 20)  # 152 => 180 => 20
        nine = malloc(self.store, 20)  # 180 => 208 => 20

        # assert that the start of the blocks make sense
        self.assertEqual(0, one)
        self.assertEqual(28, two)
        self.assertEqual(41, three)
        self.assertEqual(69, four)
        self.assertEqual(97, five)
        self.assertEqual(108, six)
        self.assertEqual(136, seven)
        self.assertEqual(152, eight)
        self.assertEqual(180, nine)

        # assert that the memory block is as expected
        memory = self.instance.exports(self.store)["malloc_memory"]
        allocated_block = memory.data_ptr(self.store)[0:nine + 28]
        allocated_block = [
            allocated_block[one:two],
            allocated_block[two:three],
            allocated_block[three:four],
            allocated_block[four:five],
            allocated_block[five:six],
            allocated_block[six:seven],
            allocated_block[seven:eight],
            allocated_block[eight:nine],
            allocated_block[nine: nine + 28]
        ]
        expected_block = [
            [1, 0, 0, 0, 255, 255, 255, 255, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 255, 255, 255, 255, 5, 0, 0, 0, 0],
            [1, 0, 0, 0, 255, 255, 255, 255, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 255, 255, 255, 255, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 255, 255, 255, 255, 3, 0, 0],
            [1, 0, 0, 0, 255, 255, 255, 255, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 255, 255, 255, 255, 8, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 255, 255, 255, 255, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 255, 255, 255, 255, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]
        self.assertEqual(
            expected_block,
            allocated_block
        )

        free_func = self.instance.exports(self.store)["free"]
        free_func(self.store, two)     # ptr => 28 : size => 5
        free_func(self.store, four)    # ptr => 69 : size => 20
        free_func(self.store, five)    # ptr => 97 : size => 3
        free_func(self.store, seven)   # ptr => 136: size => 8
        free_func(self.store, nine)    # ptr => 180: size => 20
        free_func(self.store, one)     # ptr => 0  : size => 20

        memory = self.instance.exports(self.store)["malloc_memory"]
        allocated_block = memory.data_ptr(self.store)[0:nine + 28]

        expected_block = [
            [0, 0, 0, 0, 255, 255, 255, 255, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 69, 0, 0, 0, 5, 0, 0, 0, 0],
            [1, 0, 0, 0, 255, 255, 255, 255, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 97, 0, 0, 0, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 136, 0, 0, 0, 3, 0, 0],
            [1, 0, 0, 0, 255, 255, 255, 255, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 180, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 255, 255, 255, 255, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]
        allocated_block = [
            allocated_block[one:two],
            allocated_block[two:three],
            allocated_block[three:four],
            allocated_block[four:five],
            allocated_block[five:six],
            allocated_block[six:seven],
            allocated_block[seven:eight],
            allocated_block[eight:nine],
            allocated_block[nine: nine + 28]
        ]
        self.assertEqual(
            expected_block,
            allocated_block
        )

        memory = self.instance.exports(self.store)["malloc_memory"]
        memory_page = memory.data_ptr(self.store)[0:64000]
        print(allocated_block)
        block = MemoryBlock(memory_page, 0)
        print(block.check_free(memory_page[three:four]))

        # # first realloc is going to be seven with a size of 8
        # outcome = malloc(self.store, 1)
        # print("here is the first realloc: ", outcome)
        # get_first_freed = self.instance.exports(self.store)["get_first_freed"]
        # print(get_first_freed(self.store))
        #
        # is_greater_than = self.instance.exports(self.store)["is_greater_than"]
        # print(is_greater_than(self.store, 4, 3))



if __name__ == '__main__':
    main()

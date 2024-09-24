import os
from unittest import TestCase, main

from wasmtime import Store, Module, Instance


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

    def test_malloc(self):
        malloc = self.instance.exports(self.store)["malloc"]
        outcome = malloc(self.store, 20)
        print(outcome)

        # Access the exported memory
        memory = self.instance.exports(self.store)["malloc_memory"]

        # Inspect the memory around the allocated block
        address = outcome
        allocated_block = memory.data_ptr(self.store)[0:12]

        # Print the memory contents as a list of integers
        print(f'Allocated memory block: {list(allocated_block)}')

        # Inspect the first 4 bytes of the allocated memory for example
        header_value = memory.data_ptr(self.store)[0:12]
        print(f'Header value at allocated address: {list(header_value)}')

        is_mem_free = self.instance.exports(self.store)["is_mem_free"]
        test = is_mem_free(self.store, 0)
        print(test)

        get_next_free_mem = self.instance.exports(self.store)["get_next_free_mem"]
        test = get_next_free_mem(self.store, 0)
        print(test)

        get_mem_length = self.instance.exports(self.store)["get_mem_length"]
        test = get_mem_length(self.store, 0)
        print(test)

        outcome = malloc(self.store, 20)
        print(outcome)

        # # Alternatively, you can access memory as bytearray
        # byte_array = memory.data(self.store)
        # print(f'Full memory as bytearray: {byte_array[:64]}')  # Display first 64 bytes
        # # self.assertEqual(32, outcome)
        #
        # # outcome = malloc(self.store, 20)
        # # print(outcome)


if __name__ == '__main__':
    main()

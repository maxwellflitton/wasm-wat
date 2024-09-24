import os
from unittest import TestCase, main

from wasmtime import Store, Module, Instance


class TestAdd(TestCase):

    def setUp(self):
        self.file_path = os.path.dirname(os.path.abspath(__file__))
        self.base_path = os.path.dirname(os.path.dirname(self.file_path))
        build_path = os.path.join(self.base_path, 'build')
        build_path = os.path.join(build_path, 'utils')
        self.module_path = os.path.join(build_path, 'add.wasm')
        self.store = Store()
        self.module = Module.from_file(self.store.engine, self.module_path)
        self.instance = Instance(self.store, self.module, [])

    def test_add(self):
        self.assertEqual(1 + 1, 2)
        add_func = self.instance.exports(self.store)["utils_add_add"]
        self.assertEqual(4, add_func(self.store, 1, 3))
        self.assertEqual(-2, add_func(self.store, 1, -3))


if __name__ == '__main__':
    main()

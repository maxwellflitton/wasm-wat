#!/usr/bin/env bash

# navigate to directory
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
cd $SCRIPTPATH

cd ..

# refresh the build directory
rm -rf build
mkdir build

# compile the individual modules
wat2wasm src/main.wat -o build/main.wasm
wat2wasm src/utils/add.wat -o build/add.wasm

# merge the modules
wasm-merge build/add.wasm utils_add build/main.wasm main -o build/merged.wasm

# run the merged module
wasmtime build/merged.wasm
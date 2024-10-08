#!/usr/bin/env bash

# navigate to directory
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
cd $SCRIPTPATH

cd ..

# refresh the build directory
rm -rf build
mkdir build
mkdir build/mem
mkdir build/utils
mkdir build/vars
mkdir build/vars/collections

# compile the individual modules
wat2wasm src/main.wat -o build/main.wasm
wat2wasm src/utils/add.wat -o build/utils/add.wasm
wat2wasm src/mem/malloc.wat -o build/mem/malloc.wasm

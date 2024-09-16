#!/usr/bin/env bash

# navigate to directory
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
cd $SCRIPTPATH

cd ..

rm -rf build

mkdir build
# touch ./build/build.wat

# cat src/utils/add.wat >> ./build/build.wat
# cat src/main.wat >> ./build/build.wat
# wat2wasm build/build.wat -o build/main.wasm
wasm-merge src/main.wat src/utils/add.wat -o build/merge.wasm
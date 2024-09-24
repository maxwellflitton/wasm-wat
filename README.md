# wasm-wat
toying around with wat

## Build
```bash
wat2wasm src/main.wat -o build/main.wasm
```

## Run
```bash
wasmtime build/main.wasm
```
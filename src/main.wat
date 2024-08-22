(module
  ;; Import WASI functions for writing to the console
  (import "wasi_snapshot_preview1" "fd_write"
    (func $fd_write (param i32 i32 i32 i32) (result i32)))

  ;; Define a memory section for storing strings
  (memory 1)
  (export "memory" (memory 0))

  ;; Data segment containing the string to print
  (data (i32.const 8) "Hello, World!\n")

  ;; Main function
  (func $main (export "_start")
    ;; Set up parameters for fd_write
    ;; File descriptor: 1 (stdout)
    (i32.const 1)

    ;; iov: pointer to the iovec array, which contains the string address and length
    (i32.const 16)

    ;; iovcnt: number of iovecs
    (i32.const 1)

    ;; p: pointer to where the number of bytes written will be stored
    (i32.const 28)

    ;; Call fd_write
    (call $fd_write)

    ;; Drop the result (return value) of fd_write (we're not using it here)
    drop
  )

  ;; iovec array: address and length of the string
  (data (i32.const 16)
    "\08\00\00\00\0E\00\00\00")

  ;; Storage for the number of bytes written
  (data (i32.const 28)
    "\00\00\00\00"))

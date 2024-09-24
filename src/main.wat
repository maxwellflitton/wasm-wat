(module $main
    ;; Import the required fd_write WASI function which will write the given io vectors to stdout
    ;; The function signature for fd_write is:
    ;; (File Descriptor, *iovs, iovs_len, *nwritten) -> Returns 0 on success, nonzero on error
    (import "wasi_snapshot_preview1" "fd_write" (func $fd_write (param i32 i32 i32 i32) (result i32)))
    (import "utils_add" "utils_add_add" (func $imported_add (param i32 i32) (result i32)))

    (memory 1)
    (export "memory" (memory 0))

    ;; Write 'hello world\n' to memory at an offset of 8 bytes
    ;; Note the trailing newline which is required for the text to appear
    ;; Offset 0-3: Used to store the pointer (iov_base) to the string "hello world\n".
    ;; Offset 4-7: Used to store the length (iov_len)
    (data (i32.const 8) "hello world\n")

    ;; Function to convert an integer (ASCII value) to a character and store it in memory
    (func $store_char (param $char i32) (param $offset i32)
        (i32.store8 (local.get $offset) (local.get $char))
    )

    (func $main (export "_start")
        ;; Creating a new io vector within linear memory
        ;; iovec is input/output vector which can have read and write functions
        ;; below is storing the offset of where the string is stored in memory (pointer)
        (i32.store (i32.const 0) (i32.const 8))  ;; iov.iov_base - This is a pointer to the start of the 'hello world\n' string
        ;; below is storing the length of the string
        (i32.store (i32.const 4) (i32.const 12))  ;; iov.iov_len - The length of the 'hello world\n' string

        (call $fd_write
            (i32.const 1) ;; file_descriptor - 1 for stdout
            (i32.const 0) ;; *iovs - The pointer to the iov array, which is stored at memory location 0
            (i32.const 1) ;; iovs_len - We're printing 1 string stored in an iov - so one.
            (i32.const 20) ;; nwritten - A place in memory to store the number of bytes written
        )
        drop ;; Discard the result of fd_write

        ;; Call the imported add function and drop its result
        (call $imported_add
            (i32.const 1)
            (i32.const 2)
        )
        drop ;; Discard the result of the add function

        ;; Storing three ASCII characters ('A' = 65, 'B' = 66, 'C' = 67)
        (call $store_char (i32.const 65) (i32.const 8)) ;; Store 'A' at memory offset 8
        (call $store_char (i32.const 66) (i32.const 9)) ;; Store 'B' at memory offset 9
        (call $store_char (i32.const 67) (i32.const 10)) ;; Store 'C' at memory offset 10

        ;; Store newline character '\n' at memory offset 11
        (call $store_char (i32.const 10) (i32.const 11)) ;; Store '\n' at memory offset 11

        ;; Creating a new io vector within linear memory for the ABC\n string
        (i32.store (i32.const 0) (i32.const 8))  ;; iov.iov_base - pointer to start of "ABC\n"
        (i32.store (i32.const 4) (i32.const 4))  ;; iov.iov_len - length of "ABC\n"

        ;; Print the "ABC\n" string
        (call $fd_write
            (i32.const 1) ;; file_descriptor - 1 for stdout
            (i32.const 0) ;; *iovs - pointer to the iov array, stored at memory location 0
            (i32.const 1) ;; iovs_len - 1 string stored in an iov
            (i32.const 20) ;; nwritten - a place in memory to store the number of bytes written
        )
        drop ;; Discard the result of fd_write
  )
)

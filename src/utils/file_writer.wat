(module $utils_file_writer
  ;; Import WASI functions
  (import "wasi_snapshot_preview1" "fd_write" (func $fd_write (param i32 i32 i32 i32) (result i32)))
  (import "wasi_snapshot_preview1" "path_open" 
    (func $path_open (param i32 i32 i32 i32 i32 i64 i64 i32) (result i32)))
  (import "wasi_snapshot_preview1" "fd_close" (func $fd_close (param i32) (result i32)))
;;   (import "memory")
  (memory 1)
  (export "memory" (memory 0))

  ;; Function to write a string to a file
  (func $write_to_file (param $str_offset i32) (param $str_len i32) (param $file_path_offset i32) (param $file_path_len i32)
    (local $fd i32) ;; Local variable for the file descriptor

    ;; Open the file
    (call $path_open
      (i32.const 3)    ;; fd - pre-opened directory (3 is typically the first pre-opened fd)
      (i32.const 0)    ;; dirflags - 0 (default)
      (local.get $file_path_offset)  ;; path - offset in memory where the file path string starts
      (local.get $file_path_len)  ;; path_len - length of the file path string
      (i32.const 0)    ;; oflags - 0 (default)
      (i64.const 0x0000000000000002) ;; fs_rights_base - write only
      (i64.const 0)    ;; fs_rights_inheriting - 0 (default)
      (i32.const 0)    ;; fdflags - 0 (default)
      (local.tee $fd)  ;; Store the file descriptor in local variable
    )
    
    ;; Check if file was opened successfully
    (if (i32.eqz (local.get $fd))
      (then
        ;; Handle error (unreachable in this example)
        unreachable
      )
    )

    ;; Set up the iovec structure in memory for the string
    (i32.store (i32.const 0) (local.get $str_offset))  ;; iov.iov_base - pointer to start of the string
    (i32.store (i32.const 4) (local.get $str_len))     ;; iov.iov_len - length of the string

    ;; Write to the file using the obtained file descriptor
    (call $fd_write
      (local.get $fd)  ;; file_descriptor - fd of the opened file
      (i32.const 0)    ;; *iovs - pointer to the iov array, stored at memory location 0
      (i32.const 1)    ;; iovs_len - 1 string stored in an iov
      (i32.const 20)   ;; nwritten - a place in memory to store the number of bytes written
    )
    drop ;; Discard the result of fd_write

    ;; Close the file descriptor
    (call $fd_close
      (local.get $fd)  ;; file_descriptor to close
    )
    drop ;; Discard the result of fd_close
    drop
  )

  (export "write_to_file" (func $write_to_file))
)


(i32, i32, i32, i32, i32, i64, i64, i32) -> (i32)
(i32, i32, i32, i32, i32, i64, i64, i32, i32) -> (i32)
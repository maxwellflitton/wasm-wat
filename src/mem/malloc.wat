(module $mem_malloc
  ;; Import memory
  ;;   (import "env" "memory" (memory 1))
  (memory $mem 1) 

  ;; Global variable to keep track of the next free memory address
  (global $next_free (mut i32) (i32.const 0)) ;; starts at 0

  ;; Function to allocate memory (malloc)
  (func $malloc (param $size i32) (result i32)
    (local $current_free i32)

    ;; Get the current value of the next free address
    (global.get $next_free)
    (local.set $current_free)

    ;; Increment the next free address by the requested size
    (global.set $next_free
      (i32.add
        (local.get $current_free)
        (local.get $size)
      )
    )

    ;; Return the current free address (start of allocated block)
    (local.get $current_free)
  )

  ;; Function to free memory (no-op in this simple implementation)
  (func $free (param $ptr i32)
    ;; In a real implementation, this would mark the memory at $ptr as free.
    ;; Here, it's just a placeholder.
    nop
  )

  ;; Export the malloc and free functions
  (export "malloc" (func $malloc))
  (export "free" (func $free))
)


;; (module
;;   ;; Define and export memory
;;   (memory $mem 1)
;;   (export "memory" (memory $mem))

;;   ;; Global variable to keep track of the next free memory address
;;   (global $next_free (mut i32) (i32.const 0)) ;; starts at 0

;;   ;; Function to allocate memory (malloc)
;;   (func $malloc (param $size i32) (result i32)
;;     (local $current_free i32)

;;     ;; Get the current value of the next free address
;;     (global.get $next_free)
;;     (local.set $current_free)

;;     ;; Increment the next free address by the requested size
;;     (global.set $next_free
;;       (i32.add
;;         (local.get $current_free)
;;         (local.get $size)
;;       )
;;     )

;;     ;; Return the current free address (start of allocated block)
;;     (local.get $current_free)
;;   )

;;   ;; Function to write a series of bytes to memory
;;   (func $write_bytes (param $ptr i32) (param $length i32)
;;     (local $i i32)
;;     (local $value i32)

;;     ;; Initialize index to 0
;;     (local.set $i (i32.const 0))

;;     ;; Loop to write bytes
;;     (block $exit
;;       (loop $loop
;;         ;; Exit if $i >= $length
;;         (br_if $exit
;;           (i32.ge_u (local.get $i) (local.get $length))
;;         )

;;         ;; Example value to write: Just writing the index value
;;         ;; You can replace this with any logic to write different values
;;         (local.set $value (local.get $i))

;;         ;; Write the byte to memory
;;         (i32.store8
;;           (i32.add (local.get $ptr) (local.get $i)) ;; Memory address
;;           (local.get $value)                        ;; Value to write (only lower 8 bits used)
;;         )

;;         ;; Increment index
;;         (local.set $i
;;           (i32.add (local.get $i) (i32.const 1))
;;         )

;;         ;; Repeat loop
;;         (br $loop)
;;       )
;;     )
;;   )

;;   ;; Function to read a series of bytes from memory
;;   (func $read_bytes (param $ptr i32) (param $length i32) (result i32)
;;     (local $i i32)
;;     (local $value i32)

;;     ;; Initialize index to 0
;;     (local.set $i (i32.const 0))

;;     ;; Initialize return value to 0
;;     (local.set $value (i32.const 0))

;;     ;; Loop to read bytes
;;     (block $exit
;;       (loop $loop
;;         ;; Exit if $i >= $length
;;         (br_if $exit
;;           (i32.ge_u (local.get $i) (local.get $length))
;;         )

;;         ;; Read the byte from memory
;;         (local.set $value
;;           (i32.or
;;             (local.get $value)
;;             (i32.shl
;;               (i32.load8_u
;;                 (i32.add (local.get $ptr) (local.get $i))
;;               )
;;               (i32.mul (local.get $i) (i32.const 8))
;;             )
;;           )
;;         )

;;         ;; Increment index
;;         (local.set $i
;;           (i32.add (local.get $i) (i32.const 1))
;;         )

;;         ;; Repeat loop
;;         (br $loop)
;;       )
;;     )

;;     ;; Return the combined value (for example purposes)
;;     (local.get $value)
;;   )

;;   ;; Export functions
;;   (export "malloc" (func $malloc))
;;   (export "write_bytes" (func $write_bytes))
;;   (export "read_bytes" (func $read_bytes))
;; )

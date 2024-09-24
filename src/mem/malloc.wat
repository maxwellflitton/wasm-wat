(module $mem_malloc
  ;; here is the docs for memory => https://os.phil-opp.com/heap-allocation/
  (memory $mem 1)  ;; Memory with 1 page (64 KiB)
  (export "malloc_memory" (memory $mem)) ;; Export the memory

  ;; Global variable to keep track of the next free memory address
  (global $first_free (mut i32) (i32.const 0)) ;; starts at 0
  (global $first_freed (mut i32) (i32.const -1)) ;; starts at 0
  (global $last_freed (mut i32) (i32.const -1)) ;; starts at 0


  ;; ================================ To Do =================================

  ;; [X] implement the free function
  ;; [] implement the copy data over function
  ;; [] implement the realloc function
  ;; [] build branch on malloc of existing memory block

  ;; ====================== Header extraction functions ======================

  ;; Checking to see if the memory is free
  ;; param: ptr (i32) => the pointer to the memory block
  ;; result: i32 => 1 if the memory is used, 0 if the memory is free
  (func $is_mem_free (param $ptr i32) (result i32)
    local.get $ptr
    i32.load
  )

  ;; Gets the pointer to the next free memory block.
  ;; param: ptr (i32) => the pointer to the memory block
  ;; result: i32 => the pointer to the next free memory block (0 if there is no free memory block)
  (func $get_next_free_mem (param $ptr i32) (result i32)
    local.get $ptr
    i32.const 4
    i32.add
    i32.load
  )

  ;; write a function for getting the length of the memory block
  (func $get_mem_length (param $ptr i32) (result i32)
    local.get $ptr
    i32.const 8
    i32.add
    i32.load
  )

  ;; ====================== Private Header Functions ========================


  ;; Writes the pointer to the next free memory block in the current header.
  ;; param: ptr (i32) => the pointer to the memory block
  ;; param: next_free (i32) => the pointer to the next free memory block
  (func $set_next_free_mem (param $ptr i32) (param $next_free i32)
    local.get $ptr
    call $get_next_free_mem
    local.get $next_free
    i32.store
  )

  ;; ====================== Memory allocation functions ======================

  ;; Assigns a fresh memory block.
  ;; param: size (i32) => the size of the memory block to allocate
  ;; result: i32 => the pointer to the allocated memory block
  (func $assign_fresh_memory(param $size i32) (result i32)
    (local $current_free i32)      ;; Local variable to hold the current free address
    (local $cached_free i32)       ;; Local variable to hold the current free address

    global.get $first_free
    local.set $current_free
    global.get $first_free
    local.set $cached_free

    ;; we need to assign the pointers to memory
    local.get $current_free       ;; Get the saved address
    i32.const 1                   ;; load the constant 1 onto the stack to denote the mem is used
    i32.store
    ;; increase the pointer
    local.get $current_free
    i32.const 4
    i32.add
    local.set $current_free

    ;; assign the pointer to the next free memory
    local.get $current_free        ;; Get the saved address
    i32.const -1                   ;; we know this is fresh memory so the next pointer is -1
    i32.store
    ;; increase the pointer
    local.get $current_free
    i32.const 4
    i32.add 
    local.set $current_free

    local.get $current_free       ;; Get the saved address
    local.get $size               ;; Get the size parameter
    i32.store                     ;; Store the size in the memory

    local.get $current_free       ;; Get the saved address
    local.get $size               ;; Get the size parameter
    i32.add                       ;; Add the two values (current $first_free + size) ? returns the result

    global.set $first_free        ;; Update $first_free with the new value
    local.get $cached_free        ;; Return the current free address (start of allocated block)
  )

  ;; write function on storing header pointer

  ;; Function to allocate memory (malloc)
  (func $malloc (param $size i32) (result i32)
    (local $current_free i32)      ;; Local variable to hold the current free address
    (local $cached_free i32)       ;; Local variable to hold the current free address

    global.get $first_freed         ;; check to see if there is any freed memory
    i32.const -1                    ;; Load the constant -1 onto the stack
    i32.eq                          ;; Compare if $first_freed == 0
    if (result i32)                 ;; If true (no freed memory), branch to false
      local.get $size               ;; Get the size parameter
      call $assign_fresh_memory     ;; Call the assign_fresh_memory function
    else
      ;; If there is freed memory, return -1
      i32.const -1
    end
  )

  ;; Function to free memory (no-op in this simple implementation)
  (func $free (param $ptr i32)
    ;; check if the first free memory is -1 => no freed memory => assign the pointer to the first and last freed memory
    global.get $first_freed
    i32.const -1
    i32.eq
    ;; ensure that there are not variables on the stack at the end of the if else block
    if                              ;; There is no freed memory
      local.get $ptr                ;; set the freed pointers to this
      global.set $first_freed
      local.get $ptr
      global.set $last_freed
    else                            ;; There is freed memory => append to the last freed memory
      global.get $last_freed
      local.get $ptr
      call $set_next_free_mem
      local.get $ptr
      global.set $last_freed
    end
    local.get $ptr                ;; Get the pointer to 0 to denote it can be used
    i32.const 0
    i32.store
  )

  ;; Export the malloc and free functions
  (export "malloc" (func $malloc))
  (export "free" (func $free))
  (export "is_mem_free" (func $is_mem_free))
  (export "get_next_free_mem" (func $get_next_free_mem))
  (export "get_mem_length" (func $get_mem_length))
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

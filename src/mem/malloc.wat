(module $mem_malloc
  ;; here is the docs for memory => https://os.phil-opp.com/heap-allocation/
  (memory $mem 1)  ;; Memory with 1 page (64 KiB)
  (export "malloc_memory" (memory $mem)) ;; Export the memory

  ;; Global variable to keep track of the next free memory address
  (global $first_free (mut i32) (i32.const 0)) ;; starts at 0
  (global $first_freed (mut i32) (i32.const -1)) ;; means that there is no first freed
  (global $last_freed (mut i32) (i32.const -1)) ;; means that there is no last freed


  ;; header structure | ? free | ? next free | ? length | data |


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

  ;; Gets the length of the memory block.
  ;; param: ptr (i32) => the pointer to the memory block
  ;; result: i32 => the length of the memory block
  (func $get_mem_length (param $ptr i32) (result i32)
    local.get $ptr
    i32.const 8
    i32.add
    i32.load
  )

  (func $get_first_freed (result i32)
    global.get $first_freed
  )

  (func $is_greater_than (param $one i32) (param $two i32) (result i32)
    local.get $one 
    local.get $two 
    i32.ge_u
  )

  ;; ====================== Private Header Functions ========================


  ;; Writes the pointer to the next free memory block in the current header.
  ;; param: ptr (i32) => the pointer to the memory block
  ;; param: next_free (i32) => the pointer to the next free memory block
  (func $set_next_free_mem (param $ptr i32) (param $next_free i32)
    local.get $ptr
    i32.const 4
    i32.add
    local.get $next_free
    i32.store
  )


  ;; ====================== Private Pointer Functions =======================


;;  (func $increase_pointer_by_one)



  ;; ====================== Memory allocation functions ======================

  ;; Assigns a fresh memory block.
  ;; NOTES => updates the global $current_free
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

    ;; increase the pointer
    local.get $current_free
    i32.const 4
    i32.add
    local.set $current_free

    local.get $current_free       ;; Get the saved address
    local.get $size               ;; Get the size parameter
    i32.add                       ;; Add the two values (current $first_free + size) ? returns the result

    global.set $first_free        ;; Update $first_free with the new value
    local.get $cached_free        ;; Return the current free address (start of allocated block)
  )

  ;; write function on storing header pointer

  ;; Function to allocate memory (malloc)
  (func $malloc (param $size i32) (result i32)
    (local $cached_free i32)       ;; Local variable to hold the current free address

    global.get $first_freed         ;; check to see if there is any freed memory
    i32.const -1                    ;; Load the constant -1 onto the stack
    i32.eq                          ;; Compare if $first_freed == 0
    if                              ;; If true (no freed memory), branch to false
      local.get $size
      call $assign_fresh_memory
      local.set $cached_free
    else                            ;; will try and reallocate memory
      global.get $first_freed
      call $get_mem_length
      local.get $size
      i32.ge_u
      if
        ;; we have enough memory on the first go
        global.get $first_freed
        local.set $cached_free
        local.get $cached_free
        call $get_next_free_mem
        global.set $first_freed
      else
        ;; we need to look for next free mem
        ;; move to next ptr for cached_free
        global.get $first_freed
        call $get_next_free_mem
        local.set $cached_free ;; now at 69

        ;; this is where we loop to check the (maybe break this out into a scan function)
        ;; (loop $free_check
        ;;   local.get $cached_free
        ;;   call $get_mem_length
        ;;   local.get $size
        ;;   i32.ge_u
        ;;   if
        ;;     ;; we have enough mem
        ;;     br 1
        ;;   else
        ;;     ;; move to the next ptr
        ;;     local.get $cached_free
        ;;     call $get_next_free_mem
        ;;     local.set $cached_free
        ;;     br 1
        ;;   end
        ;;   ;; ;; check to see if there is no next free mem
        ;;   ;; local.get $cached_free
        ;;   ;; call $get_next_free_mem
        ;;   ;; i32.const -1
        ;;   ;; i32.eq
        ;;   ;; if
        ;;   ;;   ;; there is no free mem left => $assign_fresh_memory => break
        ;;   ;;   local.get $size
        ;;   ;;   call $assign_fresh_memory
        ;;   ;;   local.set $cached_free
        ;;   ;;   br 1
        ;;   ;; else
        ;;   ;;   ;; check the free mem
        ;;   ;;   local.get $size
        ;;   ;;   local.get $cached_free
        ;;   ;;   call $get_mem_length
        ;;   ;;   i32.ge_u
        ;;   ;;   if
        ;;   ;;     ;; we can realloc mem
        ;;   ;;     br 1
        ;;   ;;   else
        ;;   ;;     ;; we need to loop again
        ;;   ;;   end
        ;;   ;; end
        ;; )
      end
    end
    local.get $cached_free
  )

  ;; Function to free memory (no-op in this simple implementation)
  (func $free (param $ptr i32) (result i32)
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
    global.get $last_freed
  )

  ;; Export the malloc and free functions
  (export "set_next_free_mem" (func $set_next_free_mem))
  (export "malloc" (func $malloc))
  (export "free" (func $free))
  (export "is_mem_free" (func $is_mem_free))
  (export "get_next_free_mem" (func $get_next_free_mem))
  (export "get_mem_length" (func $get_mem_length))
  (export "get_first_freed" (func $get_first_freed))
  (export "is_greater_than" (func $is_greater_than))
)

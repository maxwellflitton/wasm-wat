(module $mem_malloc
  ;; here is the docs for memory => https://os.phil-opp.com/heap-allocation/
  (memory $mem 1)  ;; Memory with 1 page (64 KiB)
  (export "malloc_memory" (memory $mem)) ;; Export the memory

  ;; Global variable to keep track of the next free memory address
  (global $first_free (mut i32) (i32.const 0)) ;; starts at 0
  (global $first_freed (mut i32) (i32.const -1)) ;; means that there is no first freed
  (global $last_freed (mut i32) (i32.const -1)) ;; means that there is no last freed


  ;; header structure | ? free | ? next free | length | data |


  ;; ================================ To Do =================================

  ;; [X] implement the free function
  ;; [X] implement the realloc function
  ;; [] implement the copy data over function
  ;; [] implement a request for more memory from the host function
  ;; [] implement memory fragmentation (2 => start block, 3 => a one of many middle block, 4 => end block)
  ;; [] implement a read function (this will be needed for fragmented memory)

  ;; ====================== Header extraction functions ======================

  ;; Checking to see if the memory is free
  ;; param: ptr (i32) => the pointer to the memory block
  ;; result: i32 => 1 if the memory is used, 0 if the memory is free
  (func $is_mem_free (param $ptr i32) (result i32)
    local.get $ptr
    i32.load
  )

  ;; Marks the memory block as no longer free removing the pointer.
  ;; param: ptr (i32) => the pointer to the memory block
  (func $reclaim_mem_block (param $ptr i32)
    local.get $ptr
    i32.const 1
    i32.store

    i32.const 4
    local.get $ptr
    i32.add
    i32.const -1
    i32.store
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

  ;; Gets the first freed pointer to the memory block.
  ;; Notes => seems simple but this function is used for external debugging in the tests
  ;; result: i32 => the pointer to the first freed memory block
  (func $get_first_freed (result i32)
    global.get $first_freed
  )

  ;; Checks if the first value is greater than the second value.
  ;; param: one (i32) => the first value
  ;; param: two (i32) => the second value
  ;; result: i32 => 1 if the first value is greater than the second value, 0 otherwise
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
    (local $trail_free i32)        ;; To lag one behind by one to enable a stiching of the memory blocks

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

        ;; set the first freed up one
        local.get $cached_free
        call $get_next_free_mem
        global.set $first_freed

        ;; set the pointer to free
        local.get $cached_free
        call $reclaim_mem_block
      else
        ;; we need to look for next free mem
        ;; move to next ptr for cached_free
        global.get $first_freed
        local.set $trail_free

        global.get $first_freed
        call $get_next_free_mem
        local.set $cached_free

        (loop $free_scan

          ;; Check the size of the memory block
          local.get $cached_free
          call $get_mem_length
          local.get $size
          i32.ge_u
          if
            ;; we have enough mem
            local.get $trail_free
            local.get $cached_free
            call $get_next_free_mem
            call $set_next_free_mem

            local.get $cached_free
            call $reclaim_mem_block
            br 0
          else
            local.get $cached_free
            local.set $trail_free

            local.get $cached_free
            call $get_next_free_mem
            local.set $cached_free

            ;; check if the next free memory is -1 => if so then we are at the end of the free memory
            local.get $cached_free
            i32.const -1
            i32.eq
            if
              ;; assign fresh memory and exit
              local.get $size
              call $assign_fresh_memory
              local.set $cached_free
              br 0
            end

            br $free_scan
          end
        )
      end
    end
    local.get $cached_free
  )

  ;; Function to free memory.
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
  (export "mem_malloc_set_next_free_mem" (func $set_next_free_mem))
  (export "mem_malloc_malloc" (func $malloc))
  (export "mem_malloc_free" (func $free))
  (export "mem_malloc_is_mem_free" (func $is_mem_free))
  (export "mem_malloc_get_next_free_mem" (func $get_next_free_mem))
  (export "mem_malloc_get_mem_length" (func $get_mem_length))
  (export "mem_malloc_get_first_freed" (func $get_first_freed))
  (export "mem_malloc_is_greater_than" (func $is_greater_than))
)

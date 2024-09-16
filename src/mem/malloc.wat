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

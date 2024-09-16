(module $vars_string
    ;; Define a function that adds two integers
    (func $add (param $a i32) (param $b i32) (result i32)
        ;; Add the two parameters and return the result
        local.get $a
        local.get $b
        i32.add
    )

    (func $new)

    ;; Export the add function with a prefixed name to avoid clashes
    (export "utils_add_add" (func $add))
)

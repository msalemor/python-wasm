from wasmer import engine, Store, Module, Instance
from wasmer_compiler_cranelift import Compiler
import time


def print_memory(memory):
    output = []
    nth = 0
    memory_length = len(memory)

    while nth < memory_length:
        byte = memory[nth]

        if byte == 0:
            break

        output.append(byte)
        nth += 1

    print(bytes(output).decode())

    return nth


# Let's define the store, that holds the engine, that holds the compiler.
start_time = time.time()


store = Store(engine.JIT(Compiler))

# Let's compile the module to be able to execute it!
module = Module(store, open('mandelbrot.wasm', 'rb').read())

# Now the module is compiled, we can instantiate it.
instance = Instance(module)

# Call the exported `sum` function.
result = instance.exports.sum(5, 37)

print(result)  # 42!

mandel_width = 140
mandel_height = 50
mandel_iterations = 100000
mandel_out_ptr = instance.exports.mandel(
    mandel_width, mandel_height, mandel_iterations)
mandel_memory = instance.exports.memory.uint8_view(mandel_out_ptr)
out_size = print_memory(mandel_memory)
instance.exports.deallocate(mandel_out_ptr, out_size)

print("--- %s seconds ---" % (time.time() - start_time))

# Set the subject to greet.
subject = bytes('Wasmer 🐍', 'utf-8')
length_of_subject = len(subject)

# Allocate memory for the subject, and get a pointer to it.
input_pointer = instance.exports.allocate(length_of_subject)

# Write the subject into the memory.
memory = instance.exports.memory.uint8_view(input_pointer)
memory[0:length_of_subject] = subject
memory[length_of_subject] = 0  # C-string terminates by NULL.

# Run the `greet` function. Give the pointer to the subject.
output_pointer = instance.exports.greet(input_pointer)

# Read the result of the `greet` function.
memory = instance.exports.memory.uint8_view(output_pointer)
length_of_output = print_memory(memory)

# Deallocate the subject, and the output.
instance.exports.deallocate(input_pointer, length_of_subject)
instance.exports.deallocate(output_pointer, length_of_output)

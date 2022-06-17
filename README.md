# Calling WASM from Python using WASMER

## Credits

- WASM
  - https://webassembly.org/
- Wasmer for Python
  - https://wasmer.io/posts/wasmer-python-embedding-1.0
  - https://github.com/wasmerio/wasmer-python/tree/master/examples/appendices
- Mandelbrot implementation in Rust
  - https://gist.github.com/jramb/2394146

## What is WASM?

From the WebAssembly.org site:

"WebAssembly (abbreviated Wasm) is a binary instruction format for a stack-based virtual machine. Wasm is designed as a portable compilation target for programming languages, enabling deployment on the web for client and server applications."

## What is WASMER for Python?

From the Wasmer for Python docs:

"The wasmer package brings the required API to execute WebAssembly modules. In a nutshell, wasmer compiles the WebAssembly module into compiled code, and then executes it. wasmer is designed to work in various environments and platforms: From nano single-board computers to large and powerful servers, including more exotic ones. To address those requirements, Wasmer provides 2 engines and 3 compilers."

## What can I gain from using WASM in Python?

### Performance

Mandelbrot settings:

- Width: 140
- Height: 50
- Iterations: 100000

Average Measurements:

- Native Python: 22s
- Using the WASM implenetation: 0.6s

### Portability

- The WASM module can be run from any operating system 
- It be embedded in different languages (C#, Javascript, Go, Java, etc.)


## Maldebrot Python implementation calling WASM

```Python
# main.py
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

start_time = time.time()

# Let's define the store, that holds the engine, that holds the compiler.
store = Store(engine.JIT(Compiler))

# Let's compile the module to be able to execute it!
module = Module(store, open('mandelbrot.wasm', 'rb').read())

# Now the module is compiled, we can instantiate it.
instance = Instance(module)

# Call the exported `sum` function.
result = instance.exports.sum(5, 37)

print(result)  # 42!

mandel_width = 140
mandel_height = 70
mandel_iterations = 100000
mandel_out_ptr = instance.exports.mandel(
    mandel_width, mandel_height, mandel_iterations)
mandel_memory = instance.exports.memory.uint8_view(mandel_out_ptr)
out_size = print_memory(mandel_memory)
instance.exports.deallocate(mandel_out_ptr, out_size)

print("--- %s seconds ---" % (time.time() - start_time))
```

## Native Python Mandelbrot Implementation

```Python
# mandelbrot.py
from util import StringBuilder


def __mandelzahl(cx: float, cy: float, max: int):
    zx = float(cx)
    zy = float(cy)
    i = 1
    x2 = zx * zx
    y2 = zy * zy

    while i < max and (x2 + y2) < 4.0:
        zy = zx * zy * 2.0 + cy
        zx = x2 - y2 + cx
        i += 1
        x2 = zx * zx
        y2 = zy * zy

    if i >= max:
        return -1
    else:
        return i


def mandel(w: int, h: int, max: int):
    sb = StringBuilder()
    step_h = 2.0 / float(h)
    step_w = 3.0 / float(w)

    for _h in range(0, h):
        y = -1.0 + float(_h) * step_h
        for _w in range(0, w):
            x = -2.0 + float(_w) * step_w
            mz = __mandelzahl(x, y, max)
            if mz > 0:
                sb.Add('-')
            else:
                sb.Add('*')
        sb.Add("\n")

    return sb
```

```python
# main.py
import time
import mandelbrot


def main():
    mandel_width = 140
    mandel_height = 50
    mandel_iterations = 100000

    start_time = time.time()
    print(mandelbrot.mandel(mandel_width, mandel_height, mandel_iterations))
    print("--- %s seconds ---" % (time.time() - start_time))


if __name__ == '__main__':
    main()
```

## Rust Mandelbrot WASM implementation

```Rust
type Fl = f32; // f32 is slightly faster than f64

fn mandelzahl(cx: Fl, cy: Fl, max: i32) -> i32 {
    let mut zx = cx; // first iteration, normally starts with (0,0)
    let mut zy = cy;
    let mut i = 1;

    let mut x2 = zx * zx;
    let mut y2 = zy * zy;
    while i < max && (x2 + y2) < 4.0 {
        zy = zx * zy * 2. + cy;
        zx = x2 - y2 + cx;
        i += 1;
        x2 = zx * zx;
        y2 = zy * zy;
    }
    if i >= max {
        -1
    } else {
        i as i32
    }
}

#[no_mangle]
pub extern "C" fn mandel(w: i32, h: i32, max: i32) -> *mut c_char {
    let step_h = 2.0 / h as Fl;
    let step_w = 3.0 / w as Fl;
    let mut output = b"".to_vec();
    for _h in 0..h {
        let y = -1.0 + ((_h as Fl) * step_h);
        for _w in 0..w {
            let x = -2.0 + ((_w as Fl) * step_w);
            let mz = mandelzahl(x, y, max);
            if mz > 0 {
                output.extend(&[b'-']);
            } else {
                output.extend(&[b'*']);
            }
        }
        output.extend(&[b'\n'])
    }
    unsafe { CString::from_vec_unchecked(output) }.into_raw()
}

#[no_mangle]
pub extern "C" fn deallocate(pointer: *mut c_void, capacity: usize) {
    unsafe {
        let _ = Vec::from_raw_parts(pointer, 0, capacity);
    }
}
```

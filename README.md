# Calling WASM from Python using WASMER

## Credits

- Mandelbrot implementation in Rust
  - https://gist.github.com/jramb/2394146
- Python Wasmer
  - https://wasmer.io/posts/wasmer-python-embedding-1.0
  - https://github.com/wasmerio/wasmer-python/tree/master/examples/appendices

## Performance

Mandelbrot settings:

- Width: 140
- Height: 50
- Iterations: 100000

Average Measurements:

- Native Python: 22s
- Using the WASM implenetation: 0.6s

## Calling WASM from Python

```Python
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

## Rust WASM implementation

```Rust
type Fl = f32; // f32 is slightly faster than f64

//fn debugvar(s: String, v:int) {
//// extern crate debug;
//println!("Type of {} is {} [{:?}]", s, v, v);
//}

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
    //let mut res = String::from("");
    let mut output = b"".to_vec();
    for _h in 0..h {
        let y = -1.0 + ((_h as Fl) * step_h);
        for _w in 0..w {
            let x = -2.0 + ((_w as Fl) * step_w);
            let mz = mandelzahl(x, y, max);
            //print!("{}", if mz > 0 { '-' } else { '*' });
            if mz > 0 {
                output.extend(&[b'-']);
            } else {
                output.extend(&[b'*']);
            }
        }
        //println!("");
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

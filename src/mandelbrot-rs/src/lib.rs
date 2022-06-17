use std::ffi::{CStr, CString};
use std::mem;
use std::os::raw::{c_char, c_void};
//use wasm_bindgen::prelude::*;

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
pub extern "C" fn sum(x: i32, y: i32) -> i32 {
    x + y
}

#[no_mangle]
pub extern "C" fn allocate(size: usize) -> *mut c_void {
    let mut buffer = Vec::with_capacity(size);
    let pointer = buffer.as_mut_ptr();
    mem::forget(buffer);

    pointer as *mut c_void
}

#[no_mangle]
pub extern "C" fn deallocate(pointer: *mut c_void, capacity: usize) {
    unsafe {
        let _ = Vec::from_raw_parts(pointer, 0, capacity);
    }
}

#[no_mangle]
pub extern "C" fn greet(subject: *mut c_char) -> *mut c_char {
    let subject = unsafe { CStr::from_ptr(subject).to_bytes().to_vec() };
    let mut output = b"Hello, ".to_vec();
    output.extend(&subject);
    output.extend(&[b'!']);

    unsafe { CString::from_vec_unchecked(output) }.into_raw()
}
#[cfg(test)]

mod tests {
    #[test]
    fn it_works() {
        let result = 2 + 2;
        assert_eq!(result, 4);
    }
}

# Build the WASM file
cargo build --release --target=wasm32-unknown-unknown
export rs_build="target/wasm32-unknown-unknown/release/"
export target="../mandelbrot-py-wasm/"
# Copy the WASM file to the python folder
cp ${rs_build}mandelbrot_rs.wasm ${target}mandelbrot.wasm


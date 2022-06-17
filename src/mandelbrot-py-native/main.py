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

from StringBuilder import StringBuilder


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


def mandel(w: int, h: int, max: int) -> str:
    sb = StringBuilder()
    step_h = 2.0 / float(h)
    step_w = 3.0 / float(w)

    for _h in range(0, h):
        y = -1.0 + float(_h) * step_h
        for _w in range(0, w):
            x = -2.0 + float(_w) * step_w
            mz = __mandelzahl(x, y, max)
            if mz > 0:
                sb.append('-')
            else:
                sb.append('*')

    return sb

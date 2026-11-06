#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""عين تتحرك -> تقترب للمنتصف -> قلب ينبض -> ينكسر -> وردة ذابلة 🥀
بدون أي مكتبات. يشتغل على Termux / Linux / Windows Terminal.
نصيحة: صغّر الخط بالقرصة قبل التشغيل لتحصل على تفاصيل أكثر."""
import math
import os
import random
import shutil
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
os.system("")  # يفعّل الألوان في ويندوز

_cols, _rows = shutil.get_terminal_size((60, 30))
W = max(24, min(_cols - 1, 96))          # أعمدة
H = max(12, min(_rows - 3, 40))          # صفوف (كل صف = بكسلين)
PW, PH = W, H * 2
CX, CY = PW / 2.0, PH / 2.0
S = min(PW * 0.46, PH * 0.62)            # نصف عرض العين بالبكسل
RESET = "\033[0m"


# ---------------- أدوات ----------------
def mix(a, b, t):
    t = 0.0 if t < 0 else 1.0 if t > 1 else t
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)


def sh(c, k):
    return (c[0] * k, c[1] * k, c[2] * k)


def ease(t):
    t = 0.0 if t < 0 else 1.0 if t > 1 else t
    return t * t * (3 - 2 * t)


def eob(t):  # ease out back (ارتداد خفيف)
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


def q(v):
    v = int(v)
    return 0 if v < 0 else 252 if v > 252 else v // 12 * 12


def render(fn):
    """كل حرف ▀ = بكسلين فوق بعض (لون الحرف + لون الخلفية)."""
    lines = []
    for r in range(H):
        y = 2 * r
        row, last = [], None
        for c in range(W):
            a, b = fn(c, y), fn(c, y + 1)
            key = (q(a[0]), q(a[1]), q(a[2]), q(b[0]), q(b[1]), q(b[2]))
            if key != last:
                row.append("\033[38;2;%d;%d;%d;48;2;%d;%d;%dm" % key)
                last = key
            row.append("▀")
        lines.append("".join(row) + RESET)
    sys.stdout.write("\033[H" + "\n".join(lines))
    sys.stdout.flush()


_last = [time.time()]


def tick(dt=0.04):
    wait = dt - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    _last[0] = time.time()


def caption(txt, delay=0.0):
    sys.stdout.write("\033[%d;1H\033[2K\033[38;2;150;150;165m%s%s" % (H + 1, txt.center(W), RESET))
    sys.stdout.flush()
    if delay:
        time.sleep(delay)


def typewriter(txt):
    for i in range(len(txt) + 1):
        caption(txt[:i].ljust(len(txt)))
        time.sleep(0.05)


# ---------------- العين ----------------
IR, PR = 0.30, 0.12
SKIN = (122, 86, 68)


def seg_d(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = 0.0 if t < 0 else 1.0 if t > 1 else t
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def make_lashes(op):
    out = []
    for i in range(-5, 6):
        x = i * 0.17
        if abs(x) > 0.93:
            continue
        y = -0.40 * op * max(0.0, 1 - x * x) ** 0.85
        ln = 0.07 + 0.06 * (1 - abs(x))
        dx, dy = x * 0.45, -1.0
        n = math.hypot(dx, dy)
        out.append((x, y, x + dx / n * ln, y + dy / n * ln))
    return out


def eye_pixel(px, py, st):
    ix, iy, s, op, lashes = st
    x = (px - CX) / (S * s) + ix
    y = (py - CY) / (S * s) + iy
    ax = abs(x)
    fa = 1 - x * x
    fp = (fa if fa > 0 else 0.0) ** 0.85
    up = 0.40 * op * fp
    lo = 0.28 * op * fp

    if ax < 1.0 and -up <= y <= lo:                       # داخل العين
        d = min(y + up, lo - y)
        shade = (0.42 + 0.58 * min(1.0, d / 0.16)) * (1 - 0.3 * ax ** 3)
        col = mix((240, 234, 230), (214, 120, 118), ax ** 5)
        dx, dy = x - ix, y - iy
        dist = math.hypot(dx, dy)
        if dist < IR:
            k = dist / IR
            ang = math.atan2(dy, dx)
            fib = 0.5 + 0.5 * math.sin(ang * 26 + k * 4)
            c = mix((190, 140, 60), (48, 118, 140), (k - 0.2) / 0.6)
            c = sh(c, 0.72 + 0.45 * fib * (1 - 0.4 * k))
            if k > 0.80:
                c = mix(c, (10, 24, 36), (k - 0.80) / 0.2)
            if dist < PR:
                c = (3, 3, 5)
            col = c
        col = sh(col, shade)
        if math.hypot(x - ix + 0.10, y - iy + 0.11) < 0.055:
            return (255, 255, 255)
        if math.hypot(x - ix - 0.10, y - iy - 0.10) < 0.028:
            return (205, 225, 255)
        return col

    vg = 1 - 0.55 * min(1.0, (((px - CX) / CX) ** 2 + ((py - CY) / CY) ** 2) * 0.55)
    col = sh(SKIN, vg)
    if ax < 1.03:
        if y < -up and (-up - y) < 0.05 + 0.02 * (1 - ax):
            return (10, 7, 8)
        if y > lo and (y - lo) < 0.022:
            return (70, 42, 38)
    if y < -0.02 and ax < 1.0:
        for a, b, c, d in lashes:
            if seg_d(x, y, a, b, c, d) < 0.012:
                return (8, 6, 7)
    yc = -up - 0.17
    if ax < 0.9 and abs(y - yc) < 0.014:
        col = sh(col, 0.62)
    yb = -0.82 + 0.26 * x * x - 0.06 * x
    if ax < 1.1 and abs(y - yb) < 0.06 * (1 - 0.4 * ax):
        col = sh((46, 30, 24), 0.75 + 0.25 * math.sin(x * 85 + y * 55))
    return col


def draw_eye(ix, iy, s, op):
    st = (ix, iy, s, op, make_lashes(op))
    render(lambda px, py: eye_pixel(px, py, st))
    tick()


def eye_phase():
    caption("watching you...")
    for t in range(24):                                   # العين تفتح
        draw_eye(0, 0, 1, ease(t / 23))
    targets = [(0, 0), (-0.45, -0.02), (0.45, 0.04), (-0.25, 0.10), (0.35, -0.04), (0, 0)]
    for a, b in zip(targets, targets[1:]):                # تتحرك يمين ويسار
        for t in range(18):
            e = ease(t / 17)
            draw_eye(a[0] + (b[0] - a[0]) * e, a[1] + (b[1] - a[1]) * e, 1, 1.0)
        for _ in range(4):
            draw_eye(b[0], b[1], 1, 1.0)
        if b == (-0.25, 0.10):                            # رمشة
            for t in range(9):
                draw_eye(b[0], b[1], 1, 1 - 0.95 * math.sin(math.pi * t / 8))
    caption("")
    for t in range(58):                                   # الاقتراب لمنتصف العين
        draw_eye(0, 0, math.exp(3.6 * ease(t / 57)), 1.0)


# ---------------- القلب ----------------
def heart_col(u, v):
    f = (u * u + v * v - 1) ** 3 - u * u * v ** 3
    if f > 0:
        return None, f
    depth = min(1.0, -f * 1.6)
    c = mix((120, 6, 28), (235, 40, 78), depth ** 0.7)
    g = math.exp(-((u + 0.5) ** 2 * 5 + (v - 0.7) ** 2 * 9))
    return mix(c, (255, 200, 215), g * 0.75), f


def crack_u(v):
    tri = abs(((v * 4) % 2) - 1)
    return (tri - 0.5) * 0.16


def heart_pixel(px, py, hs, ox=0.0, oy=0.0, ctop=None, flash=0.0):
    hs = max(hs, 0.5)
    u = (px - CX - ox) / hs
    v = -(py - CY - oy) / hs + 0.1
    c, f = heart_col(u, v)
    if c is None:
        gl = math.exp(-f * 6) * 0.5 if f < 1.5 else 0.0
        c = (210 * gl, 12 * gl, 45 * gl)
    if ctop is not None and v < ctop and f < 0.15 and abs(u - crack_u(v)) < 0.03:
        c = (255, 235, 240)
    if flash:
        c = mix(c, (255, 255, 255), flash)
    return c


def heart_phase():
    caption("")
    h0 = min(PW * 0.40, PH * 0.36)
    for t in range(26):
        hs = h0 * eob(t / 25)
        render(lambda px, py: heart_pixel(px, py, hs))
        tick()
    for t in range(60):
        k = t % 24
        b = max(math.exp(-((k - 2) ** 2) / 5.0), 0.65 * math.exp(-((k - 9) ** 2) / 7.0))
        hs = h0 * (1 + 0.08 * b)
        render(lambda px, py: heart_pixel(px, py, hs))
        tick()


def halves_pixel(px, py, hs, d, ov):
    p = ov.get((px, py))
    if p:
        return p
    pv = 1.1 * hs
    for side in (-1, 1):
        dx, dy = side * (1.0 + 0.016 * hs * d), 0.0009 * hs * d * d
        a = side * 0.02 * d
        ca, sa = math.cos(a), math.sin(a)
        qx, qy = px - CX - dx, py - CY - dy - pv
        sx = qx * ca + qy * sa
        sy = -qx * sa + qy * ca + pv
        u, v = sx / hs, -sy / hs + 0.1
        c, f = heart_col(u, v)
        if c is not None and ((u < crack_u(v)) if side < 0 else (u >= crack_u(v))):
            if abs(u - crack_u(v)) < 0.05:
                c = mix(c, (255, 230, 235), 0.6)
            return sh(c, max(0.0, 1 - d / 42.0))
    return (0, 0, 0)


def break_phase():
    h0 = min(PW * 0.40, PH * 0.36)
    caption("it hurts...")
    for t in range(16):                                   # شق يمشي بالقلب
        ct = 1.3 - 2.4 * ease(t / 15)
        sh_x = random.uniform(-1, 1) * (t / 15) * 1.2
        sh_y = random.uniform(-1, 1) * (t / 15) * 0.8
        render(lambda px, py: heart_pixel(px, py, h0, sh_x, sh_y, ct))
        tick(0.05)
    for fl in (0.9, 0.6, 0.3):
        render(lambda px, py: heart_pixel(px, py, h0, 0, 0, -1.0, fl))
        tick(0.03)
    rnd = random.Random(7)
    parts = []
    for _ in range(90):
        parts.append([CX + rnd.uniform(-.12, .12) * h0, CY + rnd.uniform(-.9, .8) * h0,
                      rnd.uniform(-1, 1) * 1.5, rnd.uniform(-2.2, 0.3),
                      rnd.choice([(255, 60, 90), (230, 30, 60), (255, 170, 190), (255, 255, 255), (150, 10, 40)])])
    for d in range(42):                                   # النصفين يسقطون + شظايا
        t = d * 0.8
        life = max(0.0, 1 - d / 42.0)
        ov = {}
        for x, y, vx, vy, col in parts:
            X, Y = int(x + vx * t + (x - CX) * 0.02 * t), int(y + vy * t + 0.09 * t * t)
            if 0 <= X < PW and 0 <= Y < PH:
                ov[(X, Y)] = sh(col, life)
        render(lambda px, py: halves_pixel(px, py, h0, d, ov))
        tick(0.04)
    caption("")


# ---------------- الوردة الذابلة ----------------
def build_rose():
    R = min(PW * 0.5, PH * 0.5)
    P = [(-0.02, 0.98), (-0.12, 0.10), (0.20, -0.70), (0.42, -0.42)]
    pts = []
    for i in range(31):
        t = i / 30.0
        m = 1 - t
        x = m ** 3 * P[0][0] + 3 * m * m * t * P[1][0] + 3 * m * t * t * P[2][0] + t ** 3 * P[3][0]
        y = m ** 3 * P[0][1] + 3 * m * m * t * P[1][1] + 3 * m * t * t * P[2][1] + t ** 3 * P[3][1]
        pts.append((x, y, 0.030 - 0.011 * t, t))
    thorns = [(pts[i][0] + s * 0.035, pts[i][1] - 0.012, 0.016, pts[i][3]) for i, s in ((9, 1), (15, -1), (21, 1))]
    allp = pts + thorns
    hc = (0.47, -0.20)
    leaves = [(-0.20, 0.42, 0.20, 0.07, 0.55), (0.17, 0.25, 0.16, 0.06, -0.65)]
    rnd = random.Random(3)
    ground_petals = [(0.15, 1.00, 0.06, 0.03, 0.3), (0.34, 1.03, 0.05, 0.028, -0.4), (-0.10, 1.04, 0.05, 0.026, 0.1)]
    buf = []
    for py in range(PH):
        row = []
        for px in range(PW):
            X = (px - CX) / R + 0.2
            Y = (py - CY) / R
            c = mix((6, 6, 16), (36, 24, 38), py / float(PH))
            vg = 1 - 0.4 * (((px - CX) / CX) ** 2) * 0.8
            c = sh(c, vg)
            if Y > 0.97:
                c = mix((44, 30, 28), (16, 11, 12), (Y - 0.97) * 4)
            for (gx, gy, a, b, rot) in ground_petals:
                dx, dy = X - gx, Y - gy
                rx = dx * math.cos(rot) + dy * math.sin(rot)
                ry = -dx * math.sin(rot) + dy * math.cos(rot)
                if (rx / a) ** 2 + (ry / b) ** 2 < 1:
                    c = (110, 14, 32)
            for (lx, ly, a, b, rot) in leaves:                # أوراق
                dx, dy = X - lx, Y - ly
                rx = dx * math.cos(rot) + dy * math.sin(rot)
                ry = -dx * math.sin(rot) + dy * math.cos(rot)
                if (rx / a) ** 2 + (ry / b) ** 2 < 1:
                    c = mix((70, 84, 36), (46, 50, 26), (rx / a + 1) / 2)
                    if rx / a > 0.55:
                        c = mix(c, (96, 66, 34), (rx / a - 0.55) / 0.45)
                    if abs(ry) < 0.009:
                        c = sh(c, 1.35)
            best, bw, bt = 9.0, 1.0, 0.0                     # الساق
            for (sx, sy, w, t) in allp:
                d = math.hypot(X - sx, Y - sy)
                if d - w < best - bw:
                    best, bw, bt = d, w, t
            if best < bw:
                c = sh(mix((30, 62, 34), (80, 80, 40), bt ** 1.5), 1 - 0.45 * (best / bw) ** 2)
            dx, dy = X - hc[0], Y - hc[1]                     # رأس الوردة
            d = math.hypot(dx, dy)
            ang = math.atan2(dy, dx)
            edge = 0.21 * (1 + 0.10 * math.sin(ang * 5 + 1) + 0.07 * math.sin(ang * 9))
            if d < edge:
                rr = d / edge
                ring = 0.5 + 0.5 * math.sin(rr * 11 + ang * 1.5)
                c = mix((52, 5, 16), (150, 20, 42), ring * (1 - 0.35 * rr))
                c = mix(c, (78, 44, 30), max(0.0, (rr - 0.78) / 0.22) * 0.8)
                c = sh(c, 0.85 + 0.3 * (-(dx + dy) * 0.5) / edge)
                if abs(math.sin(rr * 11 + ang * 1.5)) < 0.07 or rr < 0.1:
                    c = sh(c, 0.55)
            row.append(c)
        buf.append(row)
    pet = []
    for _ in range(11):
        pet.append((hc[0] + rnd.uniform(-.13, .13), hc[1] + rnd.uniform(-.05, .1), rnd.uniform(0, 45),
                    rnd.uniform(0.007, 0.012), rnd.uniform(.04, .1), rnd.uniform(0, 6)))
    return buf, pet, R


def rose_phase():
    caption("")
    sys.stdout.write("\033[2J")
    buf, pet, R = build_rose()
    rx_, ry_ = max(2.0, 0.06 * R), max(1.3, 0.035 * R)
    for t in range(18):                                    # ظهور تدريجي
        k = ease(t / 17)
        render(lambda px, py: sh(buf[py][px], k))
        tick()
    for t in range(100):                                   # بتلات تتساقط
        ov = {}
        for (x0, y0, delay, spd, sway, ph) in pet:
            tt = t - delay
            if tt <= 0:
                continue
            Y = min(1.0, y0 + spd * tt + 0.00012 * tt * tt)
            X = x0 + (sway * math.sin(tt * 0.12 + ph) + 0.002 * tt if Y < 1.0 else 0)
            ang = 0.6 * math.sin(tt * 0.1 + ph) if Y < 1.0 else 0.2
            ca, sa = math.cos(ang), math.sin(ang)
            cx, cy = (X - 0.2) * R + CX, Y * R + CY
            for dx in range(-5, 6):
                for dy in range(-4, 5):
                    a = dx * ca + dy * sa
                    b = -dx * sa + dy * ca
                    if (a / rx_) ** 2 + (b / ry_) ** 2 < 1:
                        ov[(int(cx) + dx, int(cy) + dy)] = (128 - 20 * (b > 0), 16, 36)
        render(lambda px, py: ov.get((px, py)) or buf[py][px])
        tick(0.05)
    typewriter("even the most beautiful things fade...  🥀")


def main():
    sys.stdout.write("\033[2J\033[?25l")
    try:
        eye_phase()
        heart_phase()
        break_phase()
        rose_phase()
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write(RESET + "\033[?25h\033[%d;1H\n" % (H + 3))


if __name__ == "__main__":
    main()

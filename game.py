import ast
from brus16_dsl import comp
from brus16_asm import assemble, save
from brus16_cfg import *


def to_rgb565(r, g, b):
    r5 = (r >> 3) & 0x1f
    g6 = (g >> 2) & 0x3f
    b5 = (b >> 3) & 0x1f
    return (r5 << 11) | (g6 << 5) | b5


def get_rect_addr(rect, offs=0):
    return RECT_MEM + rect * RECT_SIZE + offs


GRASS_DATA = [1, 0, 0, SCREEN_W, SCREEN_H, to_rgb565(0x3a, 0x66, 0x1c)]

ROAD0_W = 225
ROAD1_W = 180
ROAD2_W = 150

ROAD0_DATA = [1, (SCREEN_W - ROAD0_W) // 2, 0, ROAD0_W, SCREEN_H, to_rgb565(0x33, 0x80, 0x00)]
ROAD1_DATA = [1, (SCREEN_W - ROAD1_W) // 2, 0, ROAD1_W, SCREEN_H, to_rgb565(0x80, 0x80, 0x80)]
ROAD2_DATA = [1, (SCREEN_W - ROAD2_W) // 2, 0, ROAD2_W, SCREEN_H, to_rgb565(0x99, 0x99, 0x99)]

LINE_RECT = 4
LINE_PARTS = 4
LINE_W = 4
LINE_H = 42
LINE_GAP = (SCREEN_H - LINE_PARTS * LINE_H) // (LINE_PARTS - 1)
LINE_DATA = []
for i in range(LINE_PARTS):
    LINE_DATA += [1, (SCREEN_W - LINE_W) // 2, i * (LINE_H + LINE_GAP),
                  LINE_W, LINE_H, to_rgb565(0xe6, 0xe6, 0xe6)]

CROSSING_RECT = LINE_RECT + LINE_PARTS
CROSSING_PARTS = 5
CROSSING_W = LINE_W * 2
CROSSING_H = LINE_H
CROSSING_GAP = CROSSING_W * 3
CROSSING = [
    1, 252, 218, CROSSING_W, CROSSING_H, to_rgb565(0xff, 0xcc, 0x00),
    0, CROSSING_W + CROSSING_GAP, 0, CROSSING_W, CROSSING_H, to_rgb565(0xe6, 0xe6, 0xe6),
    0, (CROSSING_W + CROSSING_GAP) * 2, 0, CROSSING_W, CROSSING_H, to_rgb565(0xff, 0xcc, 0x00),
    0, (CROSSING_W + CROSSING_GAP) * 3, 0, CROSSING_W, CROSSING_H, to_rgb565(0xe6, 0xe6, 0xe6),
    0, (CROSSING_W + CROSSING_GAP) * 4, 0, CROSSING_W, CROSSING_H, to_rgb565(0xff, 0xcc, 0x00),
]

HOUSE0_RECT = CROSSING_RECT + CROSSING_PARTS
HOUSE_H = 100
HOUSE0_DATA = [
    1, 60, 140, 80, HOUSE_H * 2, to_rgb565(0x55, 0x22, 0x00),
    0, -3, -3, 80,HOUSE_H * 2, to_rgb565(0xaa, 0x44, 0x00),
    0, 38 - 3, -3, 4, HOUSE_H * 2, to_rgb565(0xd4, 0x55, 0x00),
    0, 42 - 3, -3, 38, HOUSE_H * 2, to_rgb565(0x80, 0x33, 0x00)
]
HOUSE_PARTS = len(HOUSE0_DATA) // 6
HOUSE1_RECT = HOUSE0_RECT + HOUSE_PARTS
HOUSE1_DATA = HOUSE0_DATA.copy()
HOUSE1_DATA[1] = 500
HOUSE_SIZES = [HOUSE_H, HOUSE_H * 2, HOUSE_H * 3, HOUSE_H * 4]

CAR_RECT = HOUSE1_RECT + HOUSE_PARTS
CAR_DATA = [
    1, (SCREEN_W - 24) // 2 + 40, 350, 24, 9, to_rgb565(0, 0, 0),
    0, 0, 40 - 8, 24, 9, to_rgb565(0, 0, 0),
    0, 2, 0 - 8, 20, 56, to_rgb565(0xff, 0x2a, 0x2a),
    0, 2, 0 - 8, 20, 20, to_rgb565(0xff, 0x55, 0x55),
    0, 2, 15 - 8, 20, 6, to_rgb565(0xff, 0xaa, 0xaa),
    0, 2, 40 - 8, 20, 6, to_rgb565(0xff, 0xaa, 0xaa)
]
CAR_PARTS = len(CAR_DATA) // 6

SMALL_CAR_RECT = CAR_RECT + CAR_PARTS
SMALL_CAR_X = (SCREEN_W - 24) // 2 + 40
SMALL_CAR_DATA = [
    1, SMALL_CAR_X, 100, 24, 9, to_rgb565(0, 0, 0),
    0, 0, 40 - 8, 24, 9, to_rgb565(0, 0, 0),
    0, 2, 0 - 8, 20, 54, to_rgb565(0x00, 0x88, 0xaa),
    0, 2, 40 - 8, 20, 14, to_rgb565(0x00, 0x66, 0x80),
    0, 2, 15 - 8, 20, 30, to_rgb565(0x00, 0xaa, 0xd4),
    0, 4, 14, 16, 18, to_rgb565(0x00, 0x66, 0x80)
]
SMALL_CAR_PARTS = len(SMALL_CAR_DATA) // 6
SMALL_CAR_SPEEDS = [5, 7, 10, 12]
SMALL_CAR_XS = [SMALL_CAR_X, SMALL_CAR_X - 5, SMALL_CAR_X - 10, SMALL_CAR_X - 15]

BIG_CAR_RECT = SMALL_CAR_RECT + SMALL_CAR_PARTS
BIG_CAR_X = 260
BIG_CAR_DATA = [
    1, BIG_CAR_X, -200, 40, 128, to_rgb565(0x00, 0x66, 0x80),
    0, (40 - 20) // 2, 128, 20, 4, to_rgb565(0, 0, 0),
    0, 0, 155, 40, 9, to_rgb565(0, 0, 0),
    0, 2, 128 + 4, 40 - 4, 40, to_rgb565(0x00, 0x88, 0xaa),
    0, 2, 128 + 14 + 2, 40 - 4, 20, to_rgb565(00, 0x66, 0x80),
    0, 2, 128 + 14 + 15, 40 - 4, 10, to_rgb565(0x00, 0xaa, 0xd4),
    0, 5, 128 + 14 + 15, 40 - 10, 6 - 2, to_rgb565(0x00, 0x66, 0x80),
    0, 2, 128 + 14 + 16 + 8, 40 - 4, 6, to_rgb565(0x00, 0x88, 0xaa),
]
BIG_CAR_PARTS = len(BIG_CAR_DATA) // 6
BIG_CAR_SPEEDS = [2, 2, 3, 4]
BIG_CAR_XS = [BIG_CAR_X, BIG_CAR_X + 5, BIG_CAR_X + 10, BIG_CAR_X + 15]

BG_DATA = GRASS_DATA + ROAD0_DATA + ROAD1_DATA + ROAD2_DATA + \
    LINE_DATA + CROSSING + HOUSE0_DATA + HOUSE1_DATA + CAR_DATA + \
    SMALL_CAR_DATA + BIG_CAR_DATA

MAX_SPEED = 2000
ACCEL = 10
BRAKE = 20
SLIDE = 30


game = f'''
def setup():
    set_fp({KEY_MEM})
    bg()
    while 1:
        update()
        wait()


def bg():
    copy(bg_data, {RECT_MEM}, {len(BG_DATA)})


def update():
    control_my_car()
    slide_my_car()
    move_bg()
    move_other_cars()


def control_my_car():
    if peek({KEY_MEM + KEY_UP}):
        speed_y += {ACCEL}
    if peek({KEY_MEM + KEY_DOWN}):
        speed_y -= {BRAKE}
        speed_x = 0
    if peek({KEY_MEM + KEY_LEFT}):
        if speed_y >= 100:
            speed_x = {-SLIDE}
    if peek({KEY_MEM + KEY_RIGHT}):
        if speed_y >= 100:
            speed_x = {SLIDE}
    speed_y = min({MAX_SPEED}, max(0, speed_y - 3))


def slide_my_car():
    dx = 1 + (({MAX_SPEED} - speed_y) >> 9)
    if speed_x > 0:
        speed_x = max(0, speed_x - dx)
    elif speed_x < 0:
        speed_x = min(0, speed_x + dx)
    car_x = peek({get_rect_addr(CAR_RECT, 1)})
    poke({get_rect_addr(CAR_RECT, 1)}, car_x + shra(speed_x + 4, 3))


def move_other_cars():
    car = {get_rect_addr(SMALL_CAR_RECT)}
    if (car[2] >= {SCREEN_H + 500}) | (car[2] <= -500):
        if ltu(rnd(), 1000):
            car[1] = small_car_xs[rnd() & 3]
            car[2] = -80
            small_car_speed = small_car_speeds[rnd() & 3]
    else:
        car[2] += -small_car_speed + (speed_y >> 7)
    car = {get_rect_addr(BIG_CAR_RECT)}
    if (car[2] >= {SCREEN_H}) | (car[2] <= -500):
        if ltu(rnd(), 500):
            car[1] = big_car_xs[rnd() & 3]
            car[2] = -200
            big_car_speed = big_car_speeds[rnd() & 3]
    else:
        car[2] += big_car_speed + (speed_y >> 7)


def move_bg():
    bg_speed = speed_y >> 7
    move_lines(bg_speed)
    move_crossing(bg_speed)
    move_house({get_rect_addr(HOUSE0_RECT)}, bg_speed)
    move_house({get_rect_addr(HOUSE1_RECT)}, bg_speed)


def move_crossing(speed):
    crossing = {get_rect_addr(CROSSING_RECT)}
    line = {get_rect_addr(LINE_RECT)}
    if (crossing[2] >= {SCREEN_H}) & ltu(rnd(), 1000):
        if line[2] < 0:
            crossing[2] = line[2] - {CROSSING_H + 31}
    crossing[2] += speed


def set_house_size(house, size):
    i = 0
    while i < {HOUSE_PARTS}:
        house[4] = size
        house += 6
        i += 1


def move_house(house, speed):
    if house[2] >= {SCREEN_H}:
        if ltu(rnd(), 1000):
            set_house_size(house, house_sizes[rnd() & 3])
            house[2] = -house[4] - 10
    else:
        house[2] += speed


def move_lines(speed):
    i = 0 
    while i < {LINE_PARTS}:
        move_line(i * {RECT_SIZE} + 2)
        i += 1
    line_y += speed


def move_line(rect_y):
    if line_y >= {SCREEN_H}:
        line_y -= {SCREEN_H + LINE_GAP}
    poke({get_rect_addr(LINE_RECT)} + rect_y, line_y)
    line_y += {LINE_H + LINE_GAP}


def max(a, b):
    if a > b:
        return a
    return b


def min(a, b):
    if a < b:
        return a
    return b


def copy(src, dst, size):
    end = src + size
    while src != end:
        dst[0] = src[0]
        src += 1
        dst += 1


def rnd():
    rnd_seed ^= rnd_seed << 7
    rnd_seed ^= rnd_seed >> 9
    rnd_seed ^= rnd_seed << 8
    return rnd_seed


bg_data = {BG_DATA}
house_sizes = {HOUSE_SIZES}
small_car_xs = {SMALL_CAR_XS}
small_car_speeds = {SMALL_CAR_SPEEDS}
big_car_xs = {BIG_CAR_XS}
big_car_speeds = {BIG_CAR_SPEEDS}
rnd_seed = 1
line_y = 0
speed_x = 0
speed_y = 0
small_car_speed = 5
big_car_speed = 2
'''

asm = comp(game)
for cmd in asm:
    print(' '.join(str(x) for x in cmd))
labels, code, data = assemble(asm)
print(labels)
print(len(code), len(data))
save('game.bin', code, data)

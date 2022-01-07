import pygame
from pygame import gfxdraw
from math import sin, cos, atan2, sqrt, ceil, floor
from random import randint, shuffle
import numpy as np
import tempfile
import os
import shutil

# --- constants --- (UPPER_CASE names)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

BACKGROUND = (232, 248, 222)
POINTS = (7, 95, 52)
LINES = (19, 117, 71)

FPS = 30

COLORS = [(139, 69, 19),
          (160, 82, 45),
          (210, 105, 30),
          (205, 133, 63),
          (139, 69, 19),
          (128, 0, 128),
          (153, 50, 204),
          (139, 0, 139),
          (72, 61, 139),
          (65, 105, 225),
          (0, 139, 139),
          (255, 215, 0),
          (184, 134, 11),
          (255, 140, 0),
          (255, 69, 0),
          (250, 128, 114),
          (205, 92, 92),
          (128, 0, 0)]
shuffle(COLORS)

TEMP_DIR = tempfile.mkdtemp() + str(os.path.sep)


# --- classes ---

class AdvRectangle:
    def __init__(self, rectangle):
        self.rect = rectangle
        self.dragging = False


class LineComb:
    def __init__(self, line1, line2):
        self.line1 = line1
        self.line2 = line2

    def get_comb_line(self, t):
        new_line = Line(self.line1.get_point(t), self.line2.get_point(t))
        return new_line


class Line:
    def __init__(self, init, end):
        self.init = init
        self.end = end
        self.points = get_points(init[0], init[1], end[0], end[1])

    def get_point(self, t):
        index = ceil(t * (len(self.points) - 1))
        return self.points[index]

    def __str__(self):
        return "( init:" + str(self.init) + \
               " | end:" + str(self.end) + \
               " | p_count:" + str(len(self.points)) + " )"

    def __repr__(self):
        return self.__str__()


# --- functions --- (lower_case names)

def get_rectangle_colliding(pos):
    for adv in rect_list:
        if adv.rect.collidepoint(pos):
            return adv
    return None


def get_rectangle_dragging():
    for adv in rect_list:
        if adv.dragging:
            return adv
    return None


def draw_circle(surface, color, center, width):
    gfxdraw.aacircle(surface, int(center[0]), int(center[1]), int(width), color)
    gfxdraw.filled_circle(surface, int(center[0]), int(center[1]), int(width), color)


# This came from stackOverflow, cant find the link but trust me
def draw_line(window, color, init, end, thickness):
    center = ((end[0] + init[0]) / 2, (end[1] + init[1]) / 2)
    length = sqrt(pow(init[0] - end[0], 2) + pow(init[1] - end[1], 2))
    angle = atan2(init[1] - end[1], init[0] - end[0])
    ul = (center[0] + (length / 2.) * cos(angle) - (thickness / 2.) * sin(angle),
          center[1] + (thickness / 2.) * cos(angle) + (length / 2.) * sin(angle))
    ur = (center[0] - (length / 2.) * cos(angle) - (thickness / 2.) * sin(angle),
          center[1] + (thickness / 2.) * cos(angle) - (length / 2.) * sin(angle))
    bl = (center[0] + (length / 2.) * cos(angle) + (thickness / 2.) * sin(angle),
          center[1] - (thickness / 2.) * cos(angle) + (length / 2.) * sin(angle))
    br = (center[0] - (length / 2.) * cos(angle) + (thickness / 2.) * sin(angle),
          center[1] - (thickness / 2.) * cos(angle) - (length / 2.) * sin(angle))

    draw_polygon(window, ul, ur, br, bl, color)


def draw_polygon(window, ul, ur, br, bl, color):
    gfxdraw.aapolygon(window, (ul, ur, br, bl), color)
    gfxdraw.filled_polygon(window, (ul, ur, br, bl), color)


def get_combinations(in_list):
    comb_list = []
    for i in range(0, len(in_list) - 1):
        # if its not the last one
        if i != (len(in_list) - 1):
            comb_list.append((in_list[i], in_list[i + 1]))
    return comb_list


def get_centers(in_list):
    out = []
    for p in in_list:
        out.append((p[0].rect.center, p[1].rect.center))
    return out


def get_random_rect():
    return AdvRectangle(pygame.rect.Rect(randint(0, screen.get_size()[0] - 20),
                                         randint(0, screen.get_size()[1] - 20), 20, 20))


def get_points(x1, y1, x2, y2):
    points = []
    issteep = abs(y2 - y1) > abs(x2 - x1)
    if issteep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
    rev = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        rev = True
    deltax = x2 - x1
    deltay = abs(y2 - y1)
    error = int(deltax / 2)
    y = y1
    ystep = None
    if y1 < y2:
        ystep = 1
    else:
        ystep = -1
    for x in range(x1, x2 + 1):
        if issteep:
            points.append((y, x))
        else:
            points.append((x, y))
        error -= deltay
        if error < 0:
            y += ystep
            error += deltax
    # Reverse the list if coordinates were reversed
    if rev:
        points.reverse()
    return points


def from_centers_to_lines(center_combs):
    new_list = []
    for pair in center_combs:
        new_list.append(Line(pair[0], pair[1]))
    return new_list


def create_line_combs(l_combs):
    new_list = []
    for c in l_combs:
        new_list.append(LineComb(c[0], c[1]))
    return new_list


def get_line_color(index):
    while index > (len(COLORS) - 1):
        COLORS.append((randint(0, 255), randint(0, 255), randint(0, 255)))
    return COLORS[index]


def get_product():
    prod = 1
    for r in rect_list:
        center = r.rect.center
        for p in center:
            prod *= p
    return prod


def draw_curve(comb):
    curve = []
    for t in np.linspace(0, 1, t_value):
        lines = from_centers_to_lines(comb)
        while len(lines) > 1:
            old_len = len(lines)
            line_combs = get_combinations(lines)
            line_combs = create_line_combs(line_combs)
            lines.clear()
            for pair in line_combs:
                new_line = pair.get_comb_line(t)
                lines.append(new_line)
                # draw_line(screen, get_line_color(old_len), new_line.init, new_line.end, 2)
        point = lines[0].get_point(t)
        curve.append(point)

    curve_points.clear()
    for c in get_combinations(curve):
        curve_points.append(c)

    draw_last_curve()


def draw_last_curve():
    for c in curve_points:
        draw_line(screen, RED, c[0], c[1], 3)


def get_distance_sum(c_list):
    sum = 0
    for p in c_list:
        dist = sqrt(pow(p[0][0] - p[1][0], 2) + pow(p[0][1] - p[1][1], 2))
        sum += dist
    return ceil(sum)


def set_t_value(comb):
    global t_value, distances
    distances = get_distance_sum(comb)
    if distances > 2000:
        t_value = 60
    else:
        t_value = floor((get_distance_sum(comb) + 300) / 40)
    return distances


def curve_draw_handling(comb):
    global old_product, last_product
    if not auto_draw:
        new_product = get_product()
        if last_product == new_product and get_rectangle_dragging() is None and not mouse_down:
            if new_product != old_product:
                draw_curve(comb)
            else:
                draw_last_curve()

            old_product = new_product
        else:
            last_product = new_product
    else:
        draw_curve(comb)


def animate(comb_):
    global animation_pos, last_t
    if not animate_bol:
        return
    if animation_pos == 100:
        animation_pos = -1
    else:
        animation_pos += 1

    values = np.linspace(0, 1, t_value)
    index = ceil((animation_pos * (len(values) - 1)) / 100)
    t = values[index]

    lines = from_centers_to_lines(comb_)
    while len(lines) > 1:
        old_len = len(lines)
        line_combs = get_combinations(lines)
        line_combs = create_line_combs(line_combs)
        lines.clear()
        for pair in line_combs:
            new_line = pair.get_comb_line(t)
            draw_line(screen, get_line_color(old_len), new_line.init, new_line.end, 2)
            draw_circle(screen, BLACK, new_line.init, 4)
            draw_circle(screen, BLACK, new_line.end, 4)
            lines.append(new_line)

    last_line = lines[0]
    draw_circle(screen, RED, last_line.get_point(t), 5)

    last_t = t


def save_frame():
    pygame.image.save(screen, TEMP_DIR + str(animation_pos) + ".png")


def create_video():
    os.system(
        "cd " + TEMP_DIR + "&& ffmpeg -y -r 30 -i %1d.png -vf \"scale=trunc(iw/2)*2:trunc(ih/2)*2\" -vcodec libx264 "
                           "-pix_fmt yuv420p out.mp4")
    os.startfile(TEMP_DIR + "out.mp4")
    os.startfile(TEMP_DIR)


# --- main ---

# - init -

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Bézier curves")

# - objects -

last_product = 1
old_product = 1
curve_points = []

rect_list = [get_random_rect(), get_random_rect(), get_random_rect()]
t_value = 100
distances = 0
font = pygame.font.SysFont(None, 25)

auto_draw = True
animate_bol = False
animation_pos = -1
last_t = 0
record_bol = False

hide_lines = False
hide_points = False

# - mainloop -

clock = pygame.time.Clock()

running = True

while running:

    # - events -

    mouse_down = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                shutil.rmtree(TEMP_DIR)
                pygame.quit()

            elif event.key == pygame.K_DOWN:
                rect_list.pop(len(rect_list) - 1)
                change = True
            elif event.key == pygame.K_UP:
                rect_list.append(get_random_rect())

            elif event.key == pygame.K_a:
                auto_draw = not auto_draw
            elif event.key == pygame.K_n:
                animate_bol = not animate_bol
                auto_draw = False
            elif event.key == pygame.K_l:
                hide_lines = not hide_lines
            elif event.key == pygame.K_p:
                hide_points = not hide_points
            elif event.key == pygame.K_r:
                animation_pos = -1
                animate_bol = True
                record_bol = True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_down = True
                adv_rect = get_rectangle_colliding(event.pos)
                if adv_rect is not None:
                    adv_rect.dragging = True
                    mouse_x, mouse_y = event.pos
                    offset_x = adv_rect.rect.x - mouse_x
                    offset_y = adv_rect.rect.y - mouse_y

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                adv_rect = get_rectangle_dragging()
                if adv_rect is not None:
                    adv_rect.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            adv_rect = get_rectangle_dragging()
            if adv_rect is not None:
                mouse_x, mouse_y = event.pos
                adv_rect.rect.x = mouse_x + offset_x
                adv_rect.rect.y = mouse_y + offset_y

    # - draws (without updates) -

    screen.fill(BACKGROUND)

    comb = get_centers(get_combinations(rect_list))

    set_t_value(comb)

    if not hide_lines:
        for pairs in comb:
            draw_line(screen, LINES, pairs[0], pairs[1], 3)

    animate(comb)

    curve_draw_handling(comb)

    if not hide_points:
        for adv_rect in rect_list:
            draw_circle(screen, POINTS, adv_rect.rect.center, adv_rect.rect.width / 2)

    texts = ["dist: " + str(distances) + " | linspace: " + str(t_value),
             "points: " + str(len(rect_list)) + " | " + "t: " + str(round(last_t, 3)),
             "auto draw (A): " + str(auto_draw),
             "animate (N): " + str(animate_bol),
             "hide lines (L): " + str(hide_lines),
             "hide points (P): " + str(hide_points),
             "record (R): " + str(record_bol)]

    for s in texts:
        img = font.render(s, True, BLACK)
        screen.blit(img, (20, 20 * (texts.index(s) + 1)))

    pygame.display.flip()

    if record_bol:
        save_frame()
        if animation_pos == 100:
            record_bol = False
            animate_bol = False
            create_video()
            print(TEMP_DIR)
    # - constant game speed / FPS -

    clock.tick(FPS)

# - end -

pygame.quit()

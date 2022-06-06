import pygame
from pygame import mixer
import math
pygame.init()

WIDTH = 1024
HEIGHT = 512
fps = 60
field_of_view = 60
PI = math.pi
DR = PI / 180
timer = pygame.time.Clock()
screen = pygame.display.set_mode([WIDTH, HEIGHT])

hit_wall = mixer.Sound('Sounds\\hit_wall.WAV')

light_gray = (128, 128, 128)
yellow = (255, 255, 0)
white = (255, 255, 255)
black = (0, 0, 0)
green = (0, 255, 0)
red = (255, 0, 0)
dark_red = (128, 0, 0)

player_x_pos = 300
player_y_pos = 300
player_angle = 2
player_dx = math.cos(player_angle) * 5
player_dy = math.sin(player_angle) * 5

stop_fisheye = True

map_x, map_y, map_size = 8, 8, 64

world_map = [
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 1, 1, 1, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 2, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 1,
    1, 1, 1, 1, 1, 1, 1, 1
]


def get_distance(px, py, vx, vy):
    distance = math.sqrt(((vx - px) ** 2) + ((vy - py) ** 2))
    return distance


def draw_world_map(wmap, mapx, mapy, mapsize):
    block_list = []
    for y in range(mapy):
        for x in range(mapx):
            if wmap[y * mapx + x] == 1:
                color = white
            elif wmap[y * mapx + x] == 2:
                color = red
            else:
                color = black

            xo = x * mapsize
            yo = y * mapsize
            x1 = mapsize
            y1 = mapsize

            rect = pygame.draw.rect(screen, color, (xo + 1, yo + 1, x1 - 1, y1 - 1))

            block_list.append((color, rect))

    return block_list


def draw_player(player_x, player_y):
    player_square = pygame.draw.rect(screen, yellow, (player_x - 4, player_y - 4, 8, 8))
    return player_square


def draw_rays(player_angle, player_x_pos, player_y_pos, world_map, map_size):
    ray_angle = player_angle - DR * (field_of_view / 2)
    for r in range(field_of_view):
        if ray_angle < 0:
            ray_angle += 2 * PI
        if ray_angle > 2 * PI:
            ray_angle -= 2 * PI
        dof = 0
        dist_horizontal = 1000000
        horizontal_x_pos = player_x_pos
        horizontal_y_pos = player_y_pos
        if PI < ray_angle < 2 * PI:  # looking up
            ray_y_pos = ((int(player_y_pos) >> 6) << 6)
            y_delta = player_y_pos - ray_y_pos
            x_delta = y_delta/ math.tan(ray_angle - PI)
            ray_x_pos = player_x_pos - x_delta
            y_offset = -64
            x_offset = y_offset / math.tan(ray_angle - PI)

        if 0 < ray_angle < PI:  # looking down
            ray_y_pos = ((int(player_y_pos) >> 6) << 6) + 64
            y_delta = ray_y_pos - player_y_pos
            x_delta = y_delta * math.tan(PI / 2 - ray_angle)
            ray_x_pos = player_x_pos + x_delta
            y_offset = 64
            x_offset = y_offset * math.tan(PI / 2 - ray_angle)

        while dof < 8:
            if ray_angle > PI:
                map_y_pos = (ray_y_pos / 64) - 1
            else:
                map_y_pos = ray_y_pos / 64

            map_x_pos = ((int(ray_x_pos) >> 6) << 6) / 64
            map_pos = map_y_pos * 8 + map_x_pos
            if 0 < map_pos < 64:
                if world_map[int(map_pos)] > 0:
                    map_horizontal = world_map[int(map_pos)]
                    horizontal_x_pos = ray_x_pos
                    horizontal_y_pos = ray_y_pos
                    dist_horizontal = get_distance(player_x_pos, player_y_pos, horizontal_x_pos, horizontal_y_pos)
                    dof = 8
                else:
                    ray_y_pos += y_offset
                    ray_x_pos += x_offset
                    dof += 1
            else:
                dof = 8

        dof = 0
        dist_vertical = 1000000
        vertical_x_pos = player_x_pos
        vertical_y_pos = player_y_pos
        if ray_angle < PI / 2 or ray_angle > 3 * PI / 2:  # looking right
            ray_x_pos = ((int(player_x_pos) >> 6) << 6) + 64
            x_delta = ray_x_pos - player_x_pos
            y_delta = x_delta * math.tan(ray_angle)
            ray_y_pos = player_y_pos + y_delta
            x_offset = 64
            y_offset = x_offset * math.tan(ray_angle)

        if PI / 2 < ray_angle < 3 * PI / 2:  # looking left
            ray_x_pos = ((int(player_x_pos) >> 6) << 6)
            x_delta = player_x_pos - ray_x_pos
            y_delta = x_delta * math.tan(PI - ray_angle)
            ray_y_pos = player_y_pos + y_delta
            x_offset = -64
            y_offset = -1 * (x_offset * math.tan(PI - ray_angle))

        while dof < 8:
            if ray_angle < PI / 2 or ray_angle > 3 * PI / 2:
                map_x_pos = (ray_x_pos / 64)
            else:
                map_x_pos = (ray_x_pos / 64) - 1

            map_y_pos = ((int(ray_y_pos) >> 6) << 6) / 64

            map_pos = map_y_pos * 8 + map_x_pos
            if 0 < map_pos < 64:
                if world_map[int(map_pos)] > 0:
                    map_vertical = world_map[int(map_pos)]
                    vertical_x_pos = ray_x_pos
                    vertical_y_pos = ray_y_pos
                    dist_vertical = get_distance(player_x_pos, player_y_pos, vertical_x_pos, vertical_y_pos)
                    dof = 8
                else:
                    ray_y_pos += y_offset
                    ray_x_pos += x_offset
                    dof += 1
            else:
                dof = 8

        if dist_horizontal < dist_vertical:
            camera_angle = player_angle - ray_angle
            if camera_angle > 2 * PI:
                camera_angle -= 2 * PI
            if camera_angle < 0:
                camera_angle += 2 * PI
            ray_distance = dist_horizontal
            ray_distance *= math.cos(camera_angle)
            pygame.draw.line(screen, green, (player_x_pos, player_y_pos), (horizontal_x_pos, horizontal_y_pos), 3)
            line_height = ((map_size * 320) / ray_distance)
            if map_horizontal == 1:
                pygame.draw.line(screen, light_gray, (512 + (r * 512 / field_of_view), (512 - line_height) / 2),
                                 ((512 + (r * 512 / field_of_view)), (((512 - line_height) / 2) + line_height)),
                                 math.floor(512 / field_of_view))
            if map_horizontal == 2:
                pygame.draw.line(screen, dark_red, (512 + (r * 512 / field_of_view), (512 - line_height) / 2),
                                 ((512 + (r * 512 / field_of_view)), (((512 - line_height) / 2) + line_height)),
                                 math.floor(512 / field_of_view))
        else:
            camera_angle = player_angle - ray_angle
            if camera_angle > 2 * PI:
                camera_angle -= 2 * PI
            if camera_angle < 0:
                camera_angle += 2 * PI
            ray_distance = dist_vertical
            ray_distance *= math.cos(camera_angle)
            pygame.draw.line(screen, green, (player_x_pos, player_y_pos), (vertical_x_pos, vertical_y_pos), 3)
            line_height = ((map_size * 320) / ray_distance)
            if map_vertical == 1:
                pygame.draw.line(screen, white, (512 + (r * 512 / field_of_view), (512 - line_height) / 2),
                                 ((512 + (r * 512 / field_of_view)), (((512 - line_height) / 2) + line_height)),
                                 math.floor(512 / field_of_view))
            if map_vertical == 2:
                pygame.draw.line(screen, red, (512 + (r * 512 / field_of_view), (512 - line_height) / 2),
                                 ((512 + (r * 512 / field_of_view)), (((512 - line_height) / 2) + line_height)),
                                 math.floor(512 / field_of_view))

        ray_angle += DR


running = True
while running:
    timer.tick(fps)
    screen.fill(black)

    blocks = draw_world_map(world_map, map_x, map_y, map_size)

    pygame.draw.line(screen, yellow, (player_x_pos, player_y_pos),
                     (player_x_pos + player_dx * 5, player_y_pos + player_dy * 5),
                     3)

    draw_rays(player_angle, player_x_pos, player_y_pos, world_map, map_size)

    player = draw_player(player_x_pos, player_y_pos)

    for block in blocks:
        if player.colliderect(block[1]) and block[0] != black:
            player_x_pos -= player_dx
            player_y_pos -= player_dy
            hit_wall.play()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.TEXTINPUT:
            if event.text == 'w':
                player_x_pos += player_dx
                player_y_pos += player_dy
            if event.text == 'a':
                player_angle -= 0.05
                if player_angle <= 0:
                    player_angle = 2 * PI - 0.025
                player_dx = math.cos(player_angle) * 5
                player_dy = math.sin(player_angle) * 5
            if event.text == 's':
                player_x_pos -= player_dx
                player_y_pos -= player_dy
            if event.text == 'd':
                player_angle += 0.05
                if player_angle > 2 * PI:
                    player_angle = 0.025
                player_dx = math.cos(player_angle) * 5
                player_dy = math.sin(player_angle) * 5

    pygame.display.flip()

pygame.quit()

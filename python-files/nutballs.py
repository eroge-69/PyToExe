import pygame
import numpy as np
import sys

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

def generate_vertices():
    return np.array([[x, y, z, w] 
                     for x in [-1, 1] 
                     for y in [-1, 1] 
                     for z in [-1, 1] 
                     for w in [-1, 1]])

def rotation_matrix(i, j, theta):
    mat = np.identity(4)
    c, s = np.cos(theta), np.sin(theta)
    mat[i, i], mat[i, j] = c, -s
    mat[j, i], mat[j, j] = s, c
    return mat

def rotate_4d(points, angles):
    planes = [(0,1), (0,2), (0,3), (1,2), (1,3), (2,3)]
    for (i, j), theta in zip(planes, angles):
        points = points @ rotation_matrix(i, j, theta).T
    return points

def project_4d_to_3d(points, zoom):
    w = points[:, 3]
    factor = zoom / (zoom - w)
    return points[:, :3] * factor[:, np.newaxis]

def project_3d_to_2d(points, angle_x, angle_y):
    rx = np.array([[1, 0, 0],
                   [0, np.cos(angle_x), -np.sin(angle_x)],
                   [0, np.sin(angle_x),  np.cos(angle_x)]])
    ry = np.array([[np.cos(angle_y), 0, np.sin(angle_y)],
                   [0, 1, 0],
                   [-np.sin(angle_y), 0, np.cos(angle_y)]])
    rotated = points @ rx.T @ ry.T
    return rotated[:, :2], rotated[:, 2]

def get_faces():
    squares = [
        [0,1,3,2], [4,5,7,6], [0,1,5,4], [2,3,7,6],
        [0,2,6,4], [1,3,7,5], [8,9,11,10], [12,13,15,14],
        [8,9,13,12], [10,11,15,14], [8,10,14,12], [9,11,15,13],
        [0,8,9,1], [2,10,11,3], [4,12,13,5], [6,14,15,7]
    ]
    triangles = []
    for face in squares:
        triangles.append([face[0], face[1], face[2]])
        triangles.append([face[0], face[2], face[3]])
    return triangles

vertices = generate_vertices()
faces = get_faces()
angle = 0
zoom = 3
dragging = False
angle_x, angle_y = 0, 0
mouse_prev = None

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                dragging = True
                mouse_prev = pygame.mouse.get_pos()
            elif event.button == 4:
                zoom += 0.2
            elif event.button == 5:
                zoom -= 0.2
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                dragging = False
        elif event.type == pygame.MOUSEMOTION and dragging:
            x, y = pygame.mouse.get_pos()
            dx = x - mouse_prev[0]
            dy = y - mouse_prev[1]
            angle_y += dx * 0.005
            angle_x += dy * 0.005
            mouse_prev = (x, y)

    screen.fill((255, 255, 255))  # white background
    angles = [angle * f for f in [1, 0.8, 0.6, 0.4, 0.2, 0.1]]
    rotated = rotate_4d(vertices, angles)
    projected_3d = project_4d_to_3d(rotated, zoom)
    projected_2d, z_depth = project_3d_to_2d(projected_3d, angle_x, angle_y)
    projected_2d *= 150
    projected_2d += np.array([400, 300])

    light_dir = np.array([0, 0, -1])
    face_data = []

    for tri in faces:
        pts_3d = [projected_3d[i] for i in tri]
        v1 = pts_3d[1] - pts_3d[0]
        v2 = pts_3d[2] - pts_3d[0]
        normal = np.cross(v1, v2)
        normal = normal / np.linalg.norm(normal)
        brightness = np.dot(normal, light_dir)
        brightness = max(0.1, brightness)
        color = (int(50 * brightness), int(200 * brightness), int(255 * brightness))
        avg_z = np.mean([z_depth[i] for i in tri])
        pts_2d = [projected_2d[i] for i in tri]
        face_data.append((avg_z, pts_2d, color))

    face_data.sort(key=lambda x: x[0], reverse=True)
    for _, pts, color in face_data:
        pygame.draw.polygon(screen, color, pts, 0)

    pygame.display.flip()
    clock.tick(60)
    angle += 0.01

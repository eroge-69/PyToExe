import os
import sys
import numpy as np
import trimesh
import imageio
import multiprocessing
from scipy.spatial import cKDTree
from scipy.ndimage import gaussian_filter

def load_mesh(path):
    mesh = trimesh.load(path, force='mesh')
    if not isinstance(mesh, trimesh.Trimesh):
        raise ValueError("Loaded object is not a mesh")
    mesh.remove_unreferenced_vertices()
    return mesh

def save_image(path, image):
    image = np.clip(image * 255.0, 0, 255).astype(np.uint8)
    imageio.imwrite(path, image)

def hemisphere_cosine_sample(n, samples=64):
    from numpy.random import rand
    def orthonormal_basis(n):
        if abs(n[0]) > abs(n[2]):
            inv_len = 1.0 / np.sqrt(n[0] ** 2 + n[1] ** 2)
            tangent = np.array([-n[1], n[0], 0]) * inv_len
        else:
            inv_len = 1.0 / np.sqrt(n[1] ** 2 + n[2] ** 2)
            tangent = np.array([0, -n[2], n[1]]) * inv_len
        bitangent = np.cross(n, tangent)
        return tangent, bitangent
    dirs = []
    for _ in range(samples):
        u1, u2 = rand(), rand()
        r = np.sqrt(u1)
        theta = 2 * np.pi * u2
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        z = np.sqrt(1.0 - u1)
        tangent, bitangent = orthonormal_basis(n)
        sample_dir = x * tangent + y * bitangent + z * n
        dirs.append(sample_dir)
    return np.array(dirs)

def bake_ao(mesh, resolution):
    image = np.zeros((resolution[1], resolution[0]))
    directions = hemisphere_cosine_sample(np.array([0, 0, 1]), 64)
    points, face_ids = trimesh.sample.sample_surface(mesh, 100000)
    tree = cKDTree(mesh.vertices)
    for i, (pt, face_id) in enumerate(zip(points, face_ids)):
        normal = mesh.face_normals[face_id]
        occlusion = 0
        for dir in directions:
            ray = pt + dir * 0.001
            if mesh.ray.intersects_any([ray], [dir]):
                occlusion += 1
        ao = 1 - (occlusion / len(directions))
        x = int((pt[0] - mesh.bounds[0][0]) / (mesh.extents[0]) * (resolution[0] - 1))
        y = int((pt[1] - mesh.bounds[0][1]) / (mesh.extents[1]) * (resolution[1] - 1))
        image[y, x] = ao
    return gaussian_filter(image, sigma=2)

def bake_position_map(mesh, resolution):
    image = np.zeros((resolution[1], resolution[0], 3))
    points, _ = trimesh.sample.sample_surface(mesh, 100000)
    for pt in points:
        x = int((pt[0] - mesh.bounds[0][0]) / mesh.extents[0] * (resolution[0] - 1))
        y = int((pt[1] - mesh.bounds[0][1]) / mesh.extents[1] * (resolution[1] - 1))
        image[y, x] = (pt - mesh.bounds[0]) / mesh.extents
    return image

def bake_curvature(mesh, resolution):
    from trimesh.smoothing import filter_laplacian
    smooth = filter_laplacian(mesh, lamb=0.5, iterations=20)
    diff = np.linalg.norm(mesh.vertices - smooth.vertices, axis=1)
    colors = np.zeros((resolution[1], resolution[0]))
    for i, pt in enumerate(mesh.vertices):
        x = int((pt[0] - mesh.bounds[0][0]) / mesh.extents[0] * (resolution[0] - 1))
        y = int((pt[1] - mesh.bounds[0][1]) / mesh.extents[1] * (resolution[1] - 1))
        colors[y, x] = diff[i]
    return gaussian_filter(colors, sigma=2)

def bake_normal_map(mesh, resolution):
    image = np.zeros((resolution[1], resolution[0], 3))
    for i, pt in enumerate(mesh.vertices):
        normal = mesh.vertex_normals[i]
        x = int((pt[0] - mesh.bounds[0][0]) / mesh.extents[0] * (resolution[0] - 1))
        y = int((pt[1] - mesh.bounds[0][1]) / mesh.extents[1] * (resolution[1] - 1))
        image[y, x] = (normal + 1) / 2
    return gaussian_filter(image, sigma=1)

def bake_all(path, resolution=(2048, 2048)):
    mesh = load_mesh(path)
    os.makedirs("Baked_Maps", exist_ok=True)
    with multiprocessing.Pool(4) as pool:
        results = pool.starmap(
            lambda name_func: (name_func[0], name_func[1](mesh, resolution)),
            [
                ("ao", bake_ao),
                ("position", bake_position_map),
                ("normal", bake_normal_map),
                ("curvature", bake_curvature),
            ]
        )
    for name, result in results:
        save_image(f"Baked_Maps/{name}.png", result)
    print("✅ Baking complete!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python bake_maps.py model.obj")
        sys.exit(1)
    bake_all(sys.argv[1])

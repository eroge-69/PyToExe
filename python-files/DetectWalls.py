import open3d as o3d
import numpy as np
import ctypes  # An included library with Python install.

def Mbox(title, text, style):
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)
Mbox('Your title', 'Your text', 1)

def is_wall(plane_model, vertical_threshold=np.deg2rad(15)):
    # plane_model: [a, b, c, d] for ax + by + cz + d = 0
    # walls are generally vertical => normal vector should be horizontal
    normal = np.array(plane_model[:3])
    normal /= np.linalg.norm(normal)
    
    # Vertical walls have normals with z-component near 0
    angle_with_z = np.arccos(np.abs(normal[2]))  # angle between normal and z-axis
    return angle_with_z < vertical_threshold

def detect_walls_from_point_cloud(file_path, voxel_size=0.05, distance_threshold=0.02):
    print(f"Loading point cloud: {file_path}")
    pcd = o3d.io.read_point_cloud(file_path)

    Mbox("titulo","texto",1)
    # Downsample for speed
    pcd = pcd.voxel_down_sample(voxel_size=voxel_size)

    # Estimate normals
    pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

    walls = []

    print("Segmenting planes...")
    remaining_pcd = pcd
    max_iterations = 10
    for i in range(max_iterations):
        plane_model, inliers = remaining_pcd.segment_plane(
            distance_threshold=distance_threshold,
            ransac_n=3,
            num_iterations=1000
        )

        if len(inliers) < 100:
            break  # not enough points left

        inlier_cloud = remaining_pcd.select_by_index(inliers)
        outlier_cloud = remaining_pcd.select_by_index(inliers, invert=True)

        if is_wall(plane_model):
            print(f"Wall detected (iteration {i}): {plane_model}")
            walls.append(inlier_cloud)

        remaining_pcd = outlier_cloud

    if not walls:
        print("No walls detected.")
        return

    # Combine all detected walls for visualization
    wall_cloud = walls[0]
    for w in walls[1:]:
        wall_cloud += w

    wall_cloud.paint_uniform_color([1, 0, 0])  # red for walls
    o3d.visualization.draw_geometries([wall_cloud], window_name="Detected Walls")

    # Optional: Save result
    o3d.io.write_point_cloud("C:\CGC\Partners\CGC\TBC Buildings\Code\Python\Ground_Result.ply", wall_cloud)
    print("Detected walls saved to detected_walls.ply")

if __name__ == "__main__":
    # Replace with your own file path (.ply, .pcd, etc.)
    detect_walls_from_point_cloud("C:\CGC\Partners\CGC\TBC Buildings\Code\Python\Ground.ply")

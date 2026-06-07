
import os
import cv2
import torch
import numpy as np
import open3d as o3d
from transformers import AutoImageProcessor, AutoModelForDepthEstimation

# ============================================================
# CONFIG
# ============================================================

#IMAGE_PATH = "/proj_root_/data_dir/2d_to_3d_img/shiva.jpg"
#IMAGE_PATH = "/proj_root_/data_dir/2d_to_3d_img/sistina.jpg"
IMAGE_PATH = "/proj_root_/data_dir/2d_to_3d_img/jaipur.jpg"
OUTPUT_MESH = "/proj_root_/data_dir/2d_to_3d_img/mesh_jaipur_1.obj"
OUTPUT_PCD = "/proj_root_/data_dir/2d_to_3d_img/mesh_jaipur_1.ply"

#MODEL_NAME = "LiheYoung/depth-anything-small-hf"
MODEL_NAME = "depth-anything/Depth-Anything-V2-Small-hf"

# image_processor = AutoImageProcessor.from_pretrained("depth-anything/Depth-Anything-V2-Small-hf")
# model = AutoModelForDepthEstimation.from_pretrained("depth-anything/Depth-Anything-V2-Small-hf", device_map="auto")


DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print(f"\nUsing DEVICE: {DEVICE}")

# ============================================================
# GPU INFO
# ============================================================

if DEVICE == "cuda":
    print(f"GPU : {torch.cuda.get_device_name(0)}")
    print(f"CUDA: {torch.version.cuda}")

# ============================================================
# LOAD IMAGE
# ============================================================

img_bgr = cv2.imread(IMAGE_PATH)

if img_bgr is None:
    raise Exception(f"Cannot load image: {IMAGE_PATH}")

img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

print(f"Image Shape: {img.shape}")

# ============================================================
# LOAD MODEL
# ============================================================

print("\nLoading DepthAnything model...")

processor = AutoImageProcessor.from_pretrained(MODEL_NAME)

model = AutoModelForDepthEstimation.from_pretrained(
                            MODEL_NAME
                        ).to(DEVICE)

model.eval()

print("---DepthAnything----Model loaded successfully.")

# ============================================================
# DEPTH INFERENCE
# ============================================================

print("\nRunning depth estimation...")

inputs = processor(
    images=img,
    return_tensors="pt"
).to(DEVICE)

with torch.no_grad():

    outputs = model(**inputs)
    print("----outputs.predicted_depth----.",outputs.predicted_depth)

    predicted_depth = outputs.predicted_depth

depth_map = predicted_depth.squeeze().cpu().numpy()

print("Depth map generated.")

# ============================================================
# NORMALIZE DEPTH
# ============================================================

depth_map = cv2.normalize(
    depth_map,
    None,
    0,
    255,
    cv2.NORM_MINMAX
)

depth_map = depth_map.astype(np.float32)

# ============================================================
# RESIZE IMAGE
# ============================================================

img = cv2.resize(
    img,
    (depth_map.shape[1], depth_map.shape[0])
)

# ============================================================
# DEPTH -> POINT CLOUD
# ============================================================

print("\nGenerating point cloud...")

height, width = depth_map.shape

y, x = np.meshgrid(
    np.arange(height),
    np.arange(width),
    indexing='ij'
)

#z = depth_map / 20.0 ## TODO -- Earlier FLAT Image -- Not enough Z - Depth 
z = depth_map / 3.0 ## TODO -- Earlier FLAT Image -- Not enough Z - Depth 

points = np.stack(
    (x, y, z),
    axis=-1
).reshape(-1, 3)

colors = img.reshape(-1, 3) / 255.0

mask = z.reshape(-1) > 1

points = points[mask]
colors = colors[mask]

pcd = o3d.geometry.PointCloud()

pcd.points = o3d.utility.Vector3dVector(points)

pcd.colors = o3d.utility.Vector3dVector(colors)

print(f"Point cloud size: {len(points)}")

# ============================================================
# REMOVE OUTLIERS
# ============================================================

print("\nRemoving outliers...")

pcd, ind = pcd.remove_statistical_outlier(
    nb_neighbors=20,
    std_ratio=2.0
)

# ============================================================
# NORMAL ESTIMATION
# ============================================================

print("\nEstimating normals...")

pcd.estimate_normals()

pcd.orient_normals_consistent_tangent_plane(30)

# ============================================================
# POISSON MESH
# ============================================================

print("\nGenerating mesh...")

mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
    pcd,
    depth=7
)

# ============================================================
# CLEAN MESH
# ============================================================

densities = np.asarray(densities)

density_threshold = np.quantile(densities, 0.02)

vertices_to_remove = densities < density_threshold

mesh.remove_vertices_by_mask(vertices_to_remove)

# ============================================================
# SAVE
# ============================================================

os.makedirs("results", exist_ok=True)

o3d.io.write_triangle_mesh(
    OUTPUT_MESH,
    mesh
)

print(f"\nMesh saved to: {OUTPUT_MESH}")

# ============================================================
# VISUALIZE
# ============================================================

print(mesh)
print(mesh.get_axis_aligned_bounding_box())


mesh.compute_vertex_normals()

o3d.visualization.draw_geometries(
    [mesh],
    window_name="DepthAnything Mesh",
    width=1280,
    height=720,
    mesh_show_back_face=True
)




o3d.io.write_point_cloud(
    OUTPUT_PCD,
    pcd
)




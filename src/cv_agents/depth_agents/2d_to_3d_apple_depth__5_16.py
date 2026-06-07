import os

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

import cv2
import torch
import numpy as np
from PIL import Image
import open3d as o3d


from transformers import (
    DepthProImageProcessorFast,
    DepthProForDepthEstimation
)

torch.set_grad_enabled(False)
torch.cuda.empty_cache()

# =========================================================
# DEVICE SETUP
# =========================================================

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

#device = torch.device("cpu")
print(f"\nUsing Device : {device}")

# =========================================================
# MODEL LOAD
# =========================================================

MODEL_NAME = "apple/DepthPro-hf"

print("\nLoading DepthPro model...")

image_processor = DepthProImageProcessorFast.from_pretrained(
    MODEL_NAME
)

model = DepthProForDepthEstimation.from_pretrained(
                                        MODEL_NAME,
                                        device_map="auto",
                                        torch_dtype=torch.float16,
                                        low_cpu_mem_usage=True
                                    )


model = model.to(device)
model = model.half() 
model.eval()

print("Model loaded successfully.")

# =========================================================
# INPUT IMAGE
# =========================================================


#IMAGE_PATH = "/proj_root_/data_dir/2d_to_3d_img/shiva.jpg"
IMAGE_PATH = "/proj_root_/data_dir/2d_to_3d_img/cube.png"
OUTPUT_DEPTH = "/proj_root_/data_dir/2d_to_3d_img/shiva_depth_map.png" ##OUTPUT_DEPTH = "depth_map.png"
OUTPUT_DEPTH_NORM_VIZ = "/proj_root_/data_dir/2d_to_3d_img/shiva_depth_norm_map.png" #
##depth_vis
OUTPUT_COLOR = "/proj_root_/data_dir/2d_to_3d_img/shiva_depth_colormap.png" ##"depth_colormap.png"
OUTPUT_MESH = "/proj_root_/data_dir/2d_to_3d_img/mesh_shiva_1.obj"
OUTPUT_PCD = "/proj_root_/data_dir/2d_to_3d_img/mesh_shiva_1.ply"

image_pil = Image.open(IMAGE_PATH).convert("RGB")
MAX_SIZE = 256 ### 384
image_pil.thumbnail((MAX_SIZE, MAX_SIZE))

orig_width, orig_height = image_pil.size

print(f"\nImage Size : {orig_width} x {orig_height}")

image_np = np.array(image_pil)

height, width = image_np.shape[:2]

print(f"Image Size : {width} x {height}")

# =========================================================
# PREPROCESS
# =========================================================

inputs = image_processor(
    images=image_pil,
    return_tensors="pt"
)

# Move tensors to GPU
#inputs = {k: v.to(device) for k, v in inputs.items()}


### EARLIER 
# inputs = {
#     k: v.half() if v.dtype == torch.float32 else v
#     for k, v in inputs.items()
# }

# ## BELOW NOW 
# inputs = {
#     k: v.to(device)
#     for k, v in inputs.items()
# }

inputs = {
    k: v.to(device).half()
    if v.dtype == torch.float32
    else v.to(device)
    for k, v in inputs.items()
}

# =========================================================
# INFERENCE
# =========================================================

print("\nRunning depth estimation...")

#with torch.no_grad():
with torch.inference_mode():    
    outputs = model(**inputs)

# =========================================================
# POST PROCESS
# =========================================================

post_processed_output = image_processor.post_process_depth_estimation(
    outputs,
    target_sizes=[(orig_height, orig_width)]
)

depth = post_processed_output[0]["predicted_depth"]

# Optional metadata
field_of_view = post_processed_output[0].get("field_of_view", None)
focal_length = post_processed_output[0].get("focal_length", None)

print(f"\nField of View : {field_of_view}")
print(f"Focal Length  : {focal_length}")

# =========================================================
# FLOAT DEPTH
# =========================================================

depth_np = depth.detach().cpu().numpy()

# Normalize only for visualization
depth_vis = (
    (depth_np - depth_np.min())
    / (depth_np.max() - depth_np.min())
)

depth_vis = (depth_vis * 255).astype(np.uint8)
cv2.imwrite(
    OUTPUT_DEPTH_NORM_VIZ,
    depth_vis
)

print("Saved depth_map.png--OUTPUT_DEPTH_NORM_VIZ---")


# =========================================================
# CREATE POINT CLOUD
# =========================================================
# Camera intrinsics approximation

fx = width
fy = width

cx = width / 2
cy = height / 2

points = []
colors = []

for v in range(height):

    for u in range(width):

        z = depth_np[v, u]

        # Skip invalid depth
        if z <= 0:
            continue

        x = (u - cx) * z / fx
        y = (v - cy) * z / fy

        points.append([x, y, z])

        color = image_np[v, u] / 255.0
        colors.append(color)

points = np.array(points)
colors = np.array(colors)

print(f"Point Count : {len(points)}")

# =========================================================
# OPEN3D POINT CLOUD
# =========================================================

pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(points)
pcd.colors = o3d.utility.Vector3dVector(colors)

# =========================================================
# SAVE PLY
# =========================================================

PLY_PATH = "point_cloud.ply"

o3d.io.write_point_cloud(
    PLY_PATH,
    pcd
)

print(f"PLY saved : {PLY_PATH}")


# =========================================================
# NORMALIZE DEPTH
# =========================================================

depth_min = depth.min()
depth_max = depth.max()

depth_norm = (depth - depth_min) / (depth_max - depth_min)

# Convert to uint8
depth_uint8 = (depth_norm * 255.0)

depth_uint8 = depth_uint8.detach().cpu().numpy()

depth_uint8 = depth_uint8.astype(np.uint8)

# =========================================================
# SAVE DEPTH IMAGE
# =========================================================



cv2.imwrite(
    OUTPUT_DEPTH,
    depth_uint8
)

print(f"\nDepth map saved : {OUTPUT_DEPTH}")

# =========================================================
# OPTIONAL COLOR MAP
# =========================================================

colored_depth = cv2.applyColorMap(
    depth_uint8,
    cv2.COLORMAP_INFERNO
)



cv2.imwrite(
    OUTPUT_COLOR,
    colored_depth
)

print(f"Color depth map saved : {OUTPUT_COLOR}")

# =========================================================
# CLEANUP
# =========================================================

if device.type == "cuda":
    torch.cuda.empty_cache()

print("\nDone.")




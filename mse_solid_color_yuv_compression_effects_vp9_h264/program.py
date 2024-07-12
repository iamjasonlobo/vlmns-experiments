import numpy as np
import subprocess
import matplotlib.pyplot as plt

# YUV used are all uniform per image solid color/data
# Close graphs to proceed to next step

# What this program does:
# Step 1: Creating 2 different sets of 100 hardcoded YUV frames to validate the MSE calculation
# Step 2: Creating and calculating MSE of 100 uncompressed & vp9 compressed YUV frames
    # Step 2.1: Creating a uncompressed dataset of 100 yuv frames
    # Step 2.2: Compressing the uncompressed dataset using vp9 codec with ffmpeg using libvpx-vp9 encoder in webm format
    # Step 2.3: Converting the vp9 compressed webm files back to compressed yuv format
    # Step 2.4: Calculating MSE of 100 uncompressed & vp9 compressed YUV frames
# Step 3: Creating and calculating MSE of 100 uncompressed & h264 compressed YUV frames
    # Step 3.1: Creating a uncompressed dataset of 100 yuv frames
    # Step 3.2: Compressing the uncompressed dataset using h264 codec with ffmpeg using h264_nvenc  encoder in mp4 format
    # Step 3.3: Converting the h264 compressed mp4 files back to compressed yuv format
    # Step 3.4: Calculating MSE of 100 uncompressed & h264 compressed YUV frames

# Function to create and save a YUV I420 frame
def create_yuv_frame_file(filename, width, height, y_value, u_value, v_value):
    y_channel = np.full((height, width), y_value, dtype=np.uint8)  # Y channel filled with y_value
    u_channel = np.full((height // 2, width // 2), u_value, dtype=np.uint8)  # U channel filled with u_value
    v_channel = np.full((height // 2, width // 2), v_value, dtype=np.uint8)  # V channel filled with v_value

    yuv_frame = np.concatenate((y_channel.ravel(), u_channel.ravel(), v_channel.ravel()))

    with open(filename, 'wb') as f:
        f.write(yuv_frame)

# Function to read the Y channel from a YUV I420 file
def read_y_channel(filename, width, height):
    num_y_bytes = width * height
    with open(filename, 'rb') as file:
        y_channel = np.frombuffer(file.read(num_y_bytes), dtype=np.uint8)
        y_channel = y_channel.reshape((height, width))
    return y_channel

# Function to plot the mean squared error (MSE) between two YUV images
def plot_mse(image1, image2, width, height, title):
    # List of image pairs
    image_pairs = [("frames/{}{}.yuv".format(image1, i), "frames/{}{}.yuv".format(image2, i)) for i in range(100)]

    # Array to hold mean squared errors
    mse_values = []

    # Process each pair
    for image_path1, image_path2 in image_pairs:
        y1 = read_y_channel(image_path1, width, height)
        y2 = read_y_channel(image_path2, width, height)
        # To avoid overflow, convert to float32 before squaring
        squared_diff = (y1.astype(np.float32) - y2.astype(np.float32))**2 
        mse = np.mean(squared_diff)
        mse_values.append(mse)

    # Plotting
    plt.figure(figsize=(10, 5))
    plt.plot(mse_values, marker='o', linestyle='-', color='blue')
    plt.title(f'Mean Squared Error in Y Channel Across {title}')
    plt.xlabel('Pair Index')
    plt.ylabel('MSE')
    plt.grid(True)
    plt.show()


frame_count = 100
frame_width = 640
frame_height = 576

# Step 1
# ximage
for i in range(frame_count):
    create_yuv_frame_file(f'frames/ximage{i:0d}.yuv', frame_width, frame_height, 255, 0, 0)

# yimage
for i in range(frame_count):
    if i % 3 == 0:
        create_yuv_frame_file(f'frames/yimage{i:0d}.yuv', frame_width, frame_height, 179, 0, 0)
    elif i % 3 == 1:
        create_yuv_frame_file(f'frames/yimage{i:0d}.yuv', frame_width, frame_height, 125, 0, 0) 
    else:
        create_yuv_frame_file(f'frames/yimage{i:0d}.yuv', frame_width, frame_height, 100, 0, 0)

plot_mse("ximage", "yimage", frame_width, frame_height, "2 sets of random 100 hardcoded YUV frames")


# uncompressed yuv frames (uimage)
for i in range(frame_count):
    if i % 3 == 0:
        create_yuv_frame_file(f'frames/uimage{i:0d}.yuv', frame_width, frame_height, 255, 0, 0)
    elif i % 3 == 1:
        create_yuv_frame_file(f'frames/uimage{i:0d}.yuv', frame_width, frame_height, 0, 0, 0) 
    else:
        create_yuv_frame_file(f'frames/uimage{i:0d}.yuv', frame_width, frame_height, 100, 0, 0)

#  Step 2  
# vp9 compression (vid.webm)
for i in range(0,100):
    print(f"vp9 compression {i}")
    subprocess.run(f"ffmpeg -f rawvideo -pix_fmt yuv420p -s {frame_width}x{frame_height} -i frames/uimage{i}.yuv -c:v libvpx-vp9 -pix_fmt yuv420p frames/vid{i}.webm", shell=True)

# vp9 compressed yuv frames (cvp9_image)
for i in range(0,100):
    print(f"vp9 compressed yuv {i}")
    subprocess.run(f"ffmpeg -i frames/vid{i}.webm -pix_fmt yuv420p frames/cvp9_image{i}.yuv", shell=True)

plot_mse("uimage", "cvp9_image", frame_width, frame_height, "uncompressed and vp9 compressed")

#  Step 3
# h264 compression (vid.mp4)
for i in range(0,100):
    print(f"h264 compression {i}")
    subprocess.run(f"ffmpeg -f rawvideo -pix_fmt yuv420p -s {frame_width}x{frame_height} -i frames/uimage{i}.yuv -c:v libx264 -pix_fmt yuv420p frames/vid{i}.mp4", shell=True)

# h264 compressed yuv frames (ch264_image)
for i in range(0,100):
    print(f"Processing webm {i}")
    subprocess.run(f"ffmpeg -i frames/vid{i}.mp4 -pix_fmt yuv420p frames/ch264_image{i}.yuv", shell=True)

plot_mse("uimage", "ch264_image", frame_width, frame_height, "uncompressed and h264 compressed")


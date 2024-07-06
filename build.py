import os
import json
from PIL import Image
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import threading


def generate_thumbnail(image_path, thumbnail_path):
    thread_id = threading.get_ident()  # 获取当前线程的编号
    print(f"Thread {thread_id}: Generating thumbnail for {image_path}")
    
    size = (800, 800)  # 默认缩略图尺寸
    with Image.open(image_path) as im:
        # 计算缩放比例
        width, height = im.size
        if width > height:
            new_width = size[0]
            new_height = int(size[0] * height / width)
        else:
            new_height = size[1]
            new_width = int(size[1] * width / height)
        
        # 生成缩略图
        im.thumbnail((new_width, new_height), resample=Image.LANCZOS)
        im.save(thumbnail_path, optimize=True)
    print(f"Thread {thread_id}: Thumbnail generated for {image_path}")


def generate_image_list():
    image_list = []
    script_path = os.path.dirname(os.path.abspath(__file__))  # 当前脚本的目录
    folder_path = os.path.join(script_path, "img")  # img文件夹路径
    thumbnail_folder = os.path.join(script_path, "thum")  # 缩略图文件夹路径
    
    # 如果缩略图文件夹不存在，创建它
    if not os.path.exists(thumbnail_folder):
        os.makedirs(thumbnail_folder)
    
    # 删除旧的images.json文件
    json_file_path = os.path.join(script_path, "images.json")
    if os.path.exists(json_file_path):
        os.remove(json_file_path)
    
    # 遍历img文件夹中的文件
    with ThreadPoolExecutor() as executor:
        futures = []
        for filename in os.listdir(folder_path):
            if filename.endswith(".jpg") or filename.endswith(".png"):
                image_path = os.path.join(folder_path, filename)
                thumbnail_path = os.path.join(thumbnail_folder, filename)
                future = executor.submit(generate_thumbnail, image_path, thumbnail_path)
                futures.append(future)
                image_item = {
                    "src": os.path.relpath(image_path, script_path),
                    "thumbnail": os.path.relpath(thumbnail_path, script_path)
                }
                image_list.append(image_item)
        
        # 等待所有线程完成
        for future in tqdm(futures, position=0):
            future.result()
            print("", end="\r")  # 输出换行
        
    # 生成JSON文件
    with open(json_file_path, "w") as json_file:
        json.dump(image_list, json_file, indent=4)
    
    print("Image list generated.")

# 调用函数生成图片列表JSON文件
generate_image_list()

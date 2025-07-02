"""
功能介绍
本项目是一个Python脚本，用于将指定文件夹中的所有图片文件转换为一个PDF文件。
每个图片文件将单独占据一页，并且PDF文件的名称将与文件夹名称相同。
此外，脚本还支持按照自然顺序（而不是字符串顺序）对图片文件进行排序。
"""

import os
from PIL import Image
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas
import re

# 定义一个自然排序的函数，用于对字符串进行排序
def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
    # 使用正则表达式将字符串中的数字和字母分开
    return [int(text) if text.isdigit() else text.lower()
            # 如果是数字，则将其转换为整数，否则将其转换为小写字母
            for text in re.split(_nsre, s)]

def images_to_pdf(folder_path, pdf_path):
    # 打印处理文件夹
    print(f"Processing folder: {folder_path}")
    # 获取文件夹中所有以.png、.jpg、.jpeg、.bmp、.gif结尾的文件
    images = [f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
    # 对文件进行自然排序
    images.sort(key=natural_sort_key)

    # 获取第一张图片的路径
    img_path = os.path.join(folder_path, images[0])
    # 打开第一张图片
    img = Image.open(img_path)
    # 获取图片的宽度和高度
    img_width, img_height = img.size
    # 创建一个画布，画布大小为图片的宽度和高度
    c = canvas.Canvas(pdf_path, pagesize=landscape((img_width, img_height)))
    # 获取画布的宽度和高度
    width, height = landscape((img_width, img_height))

    # 遍历文件夹中的所有图片
    for image_file in images:
        # 获取图片的路径
        image_path = os.path.join(folder_path, image_file)
        # 打开图片
        img = Image.open(image_path)
        # 获取图片的宽度和高度
        img_width, img_height = img.size
        # 打印插入图片
        print(f"Inserting image: {image_file}")
        # 计算缩放比例
        aspect_ratio = img_width / img_height
        if img_width > img_height:
            # 如果图片宽度大于高度，则将图片宽度设置为画布宽度，高度按比例缩放
            new_width = width
            new_height = width / aspect_ratio
        else:
            # 如果图片高度大于宽度，则将图片高度设置为画布高度，宽度按比例缩放
            new_height = height
            new_width = height * aspect_ratio

        # 计算位置
        x = (width - new_width) / 2
        y = (height - new_height) / 2

        # 绘制图片
        c.drawImage(image_path, x, y, new_width, new_height)

        # 添加新页面
        c.showPage()

    # 保存画布
    c.save()

# 定义一个函数，用于处理文件夹
def process_folder(root_folder, target_folder):
    # 遍历root_folder文件夹中的所有文件和文件夹
    for folder_name in os.listdir(root_folder):
        # 获取文件夹的路径
        folder_path = os.path.join(root_folder, folder_name)
        # 判断是否为文件夹
        if os.path.isdir(folder_path):
            # 获取pdf文件的名称
            pdf_name = f"{folder_name}.pdf"
            # 获取pdf文件的路径
            pdf_path = os.path.join(target_folder, pdf_name)
            # 调用images_to_pdf函数，将文件夹中的图片转换为pdf文件
            images_to_pdf(folder_path, pdf_path)

# 示例调用
root_folder = r'C:\Users\123\Downloads\test'  #本目录下为多个图片目录
target_folder = r'C:\target'
process_folder(root_folder, target_folder)

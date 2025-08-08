"""
# 交通数据下载与处理脚本

## 1. 功能概述

本脚本实现了从加州交通管理系统(PeMS)自动下载交通数据文件，并自动解压整理的功能。

### 核心功能：
- 批量下载.gz格式的交通数据文件
- 自动解压文件并保持原始文件名一致
- 支持Cookie认证和代理设置
- 多线程并发下载提高效率
- 断点续传避免重复下载

## 2. 输入配置

### 2.1 必需配置
- **Cookie信息**：用于PeMS网站认证
  COOKIES = {
  }

- **下载链接列表**：存储在[1.txt]文件中
  https://pems.dot.ca.gov/?download=495399&dnode=Clearinghouse
  https://pems.dot.ca.gov/?download=495465&dnode=Clearinghouse
  ...

### 2.2 可选配置
- **代理设置**：默认配置为Clash代理
- **并发数**：默认2个线程
- **下载目录**：`./downloads`
- **解压目录**：`./extracted`

## 3. 输出结果

### 3.1 文件结构
项目目录/
├── downloads/           # 原始.gz文件
│   ├── d07_text_station_5min_2025_03_19.txt.gz
│   └── d04_text_station_5min_2025_03_20.txt.gz
└── extracted/          # 解压后的.txt文件
    ├── d07_text_station_5min_2025_03_19.txt
    └── d04_text_station_5min_2025_03_20.txt

### 3.2 文件命名规则
- 保持与浏览器直接下载完全一致的文件名
- 下载文件：d07_text_station_5min_2025_03_19.txt.gz
- 解压文件：d07_text_station_5min_2025_03_19.txt

### 3.3 运行日志示例
开始批量下载 200 个文件
正在下载: d07_text_station_5min_2025_03_19.txt.gz
HTTP状态码: 200
  内容类型: application/x-gzip
  内容描述: attachment; filename=d07_text_station_5min_2025_03_19.txt.gz
  原始文件名: d07_text_station_5min_2025_03_19.txt.gz
下载完成: d07_text_station_5min_2025_03_19.txt.gz
  文件大小: 1250000 字节
  平均速度: 2.5 MB/s
  已解压: d07_text_station_5min_2025_03_19.txt

## 4. 使用方法

1. 配置PeMS网站Cookie
2. 确保代理(如Clash)正常运行
3. 运行脚本
4. 等待自动下载和解压完成

"""



# 在文件顶部导入所需模块
import os
import requests
from concurrent.futures import ThreadPoolExecutor
import time
import gzip
import shutil
import re

# ===== 配置部分 =====
DOWNLOAD_DIR = "./downloads"  # 下载文件保存目录
EXTRACTED_DIR = "./extracted"  # 解压后文件保存目录
MAX_THREADS = 2  # 降低并发数
# ===================

# 创建下载目录和解压目录
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(EXTRACTED_DIR, exist_ok=True)

# 浏览器般的请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Referer': 'https://pems.dot.ca.gov/',
}

# 你需要从浏览器中获取并填入的Cookie信息
COOKIES = {
# 按需自行配置
}


def read_download_links(file_path):
    """从文件中读取下载链接"""
    with open(file_path, 'r') as f:
        links = [line.strip() for line in f if line.strip()]
    return links


def format_speed(bytes_per_sec):
    """格式化下载速度显示"""
    for unit in ['B/s', 'KB/s', 'MB/s', 'GB/s']:
        if bytes_per_sec < 1024.0:
            return f"{bytes_per_sec:.2f} {unit}"
        bytes_per_sec /= 1024.0
    return f"{bytes_per_sec:.2f} TB/s"


def extract_gz_file(gz_filepath, original_filename=None):
    """解压gz文件并将内容保存为txt文件，文件名与原始文件名一致"""
    try:
        if original_filename:
            # 使用原始文件名（去掉.gz扩展名）
            if original_filename.endswith('.gz'):
                txt_filename = original_filename[:-3]  # 去掉.gz扩展名
            else:
                txt_filename = original_filename + ".txt"
        else:
            # 从gz文件名推断
            base_filename = os.path.basename(gz_filepath)
            if base_filename.endswith('.gz'):
                txt_filename = base_filename[:-3]  # 去掉.gz扩展名
            else:
                txt_filename = base_filename.replace('.gz', '') + '.txt'

        txt_filepath = os.path.join(EXTRACTED_DIR, txt_filename)

        # 解压gz文件
        with gzip.open(gz_filepath, 'rb') as f_in:
            with open(txt_filepath, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        print(f"  已解压: {txt_filename}")
        return txt_filepath
    except Exception as e:
        print(f"  解压失败 {gz_filepath}: {str(e)}")
        return None


def download_file(url):
    try:
        # 初始文件名
        filename = os.path.basename(url.split('?')[0])  # 去除URL参数
        if not filename:
            # 使用URL的参数作为文件名
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(url)
            params = parse_qs(parsed_url.query)
            download_id = params.get('download', ['unknown'])[0]
            filename = f"download_{download_id}.gz"

        filepath = os.path.join(DOWNLOAD_DIR, filename)

        # 如果文件已存在，跳过下载
        if os.path.exists(filepath):
            print(f"文件已存在，跳过: {filename}")
            # 直接解压已存在的文件
            extract_gz_file(filepath)
            return

        print(f"正在下载: {filename}")

        # 专门为Clash配置的会话
        session = requests.Session()

        # 设置代理
        proxies = {
# 按需自行配置
        }
        session.proxies = proxies
        session.trust_env = False

        # 设置Cookie和Headers
        session.cookies.update(COOKIES)
        session.headers.update(HEADERS)

        # 添加延迟避免请求过于频繁
        time.sleep(2)

        # 使用流式下载大文件
        response = session.get(url, stream=True, timeout=120)

        # 检查响应状态
        print(f"HTTP状态码: {response.status_code}")

        if response.status_code != 200:
            print(f"下载失败 {url}: HTTP状态码 {response.status_code}")
            # 保存错误响应以便分析
            error_filepath = filepath + f"_error_{response.status_code}.html"
            with open(error_filepath, 'wb') as f:
                f.write(response.content)
            print(f"  错误页面已保存为: {error_filepath}")
            return

        # 检查内容类型
        content_type = response.headers.get('content-type', '')
        content_disposition = response.headers.get('content-disposition', '')

        print(f"  内容类型: {content_type}")
        print(f"  内容描述: {content_disposition}")

        # 从content-disposition中提取文件名
        original_filename = None
        if 'filename=' in content_disposition:
            # 使用正则表达式提取文件名
            match = re.search(r'filename=([^;]+)', content_disposition)
            if match:
                original_filename = match.group(1).strip().strip('"\'')
                print(f"  原始文件名: {original_filename}")

                # 更新文件路径以使用原始文件名
                filepath = os.path.join(DOWNLOAD_DIR, original_filename)
                filename = original_filename

        # 获取文件总大小
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        start_time = time.time()
        last_time = start_time
        last_downloaded = 0

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)

                    # 每隔1秒计算并显示一次速度
                    current_time = time.time()
                    if current_time - last_time >= 1.0:
                        speed = (downloaded - last_downloaded) / (current_time - last_time)
                        progress_info = f"  {filename}: {format_speed(speed)}"
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            progress_info += f" ({percent:.1f}%)"
                        print(progress_info)

                        last_time = current_time
                        last_downloaded = downloaded

        # 计算平均下载速度
        total_time = time.time() - start_time
        file_size = os.path.getsize(filepath)

        print(f"下载完成: {filename}")
        print(f"  文件大小: {file_size} 字节")
        if total_time > 0:
            avg_speed = downloaded / total_time
            print(f"  平均速度: {format_speed(avg_speed)}")

        # 下载完成后自动解压，使用原始文件名
        if file_size > 0:
            extract_gz_file(filepath, original_filename)

    except Exception as e:
        print(f"下载失败 {url}: {str(e)}")


def extract_all_existing_files():
    """解压所有已存在的gz文件"""
    print("正在解压已存在的gz文件...")
    for filename in os.listdir(DOWNLOAD_DIR):
        if filename.endswith('.gz'):
            gz_filepath = os.path.join(DOWNLOAD_DIR, filename)
            extract_gz_file(gz_filepath)


def main():
    global DOWNLOAD_LINKS
    DOWNLOAD_LINKS = read_download_links('1.txt')  # 读取1.txt中的链接
    print(f"开始批量下载 {len(DOWNLOAD_LINKS)} 个文件")

    # 使用多线程加速下载
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(download_file, DOWNLOAD_LINKS)

    print("所有文件下载任务已完成")
    print(f"解压后的文件保存在: {EXTRACTED_DIR}")


if __name__ == "__main__":
    # 如果已经有下载的文件，先解压它们
    if os.listdir(DOWNLOAD_DIR):
        extract_all_existing_files()

    main()

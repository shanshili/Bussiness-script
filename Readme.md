# 🎲Business-scrip 

## 📚项目概述/Project Overview

`Business-scrip` 是一个用于处理办公文件的小脚本集合。这些脚本旨在简化日常办公中的一些重复性任务，提高工作效率。项目文件夹下包含多个小脚本，每个脚本专注于特定的文件处理任务。

`Business-scrip` is a collection of small scripts designed for processing office documents. These scripts aim to simplify repetitive daily office tasks, thereby improving work efficiency. The project folder contains multiple small scripts, each focusing on specific file processing tasks.

## 📚目录结构/Directory Structure

```
Business-scrip/
├── file_image_pdf.py
└── pems_downloader.py
```


## 📚脚本介绍/Script Introduction

### 📗file_image_pdf.py

#### 功能描述/Function Description

`file_image_pdf.py` 本脚本用于将指定文件夹中的所有图片文件转换为一个PDF文件。
每个图片文件将单独占据一页，并且PDF文件的名称将与文件夹名称相同。
此外，脚本还支持按照自然顺序（而不是字符串顺序）对图片文件进行排序。

`file_image_pdf.py` This script converts all image files in a specified folder into a single PDF file. Each image occupies a separate page, and the generated PDF file shares the same name as the folder. Additionally, the script supports sorting image files in natural order (rather than string order).

### 📗pems_downloader.py

#### 1. 功能描述/Function Description

本脚本实现了从加州交通管理系统(PeMS)自动下载交通数据文件，并自动解压整理的功能。

**核心功能：**

- 批量下载.gz格式的交通数据文件
- 自动解压文件并保持原始文件名一致
- 支持Cookie认证和代理设置
- 多线程并发下载提高效率
- 断点续传避免重复下载

#### 2. 输入配置

**2.1 必需配置**

- **Cookie信息**：用于PeMS网站认证
  ```python
  COOKIES = {
      '***': '******',
      '***': '******'
  }
  ```


- **下载链接列表**：存储在`1.txt`文件中
  ```
  https://pems.dot.ca.gov/?download=495399&dnode=Clearinghouse
  https://pems.dot.ca.gov/?download=495465&dnode=Clearinghouse
  ...
  ```

**2.2 可选配置**

- **代理设置**：默认配置为Clash代理
- **并发数**：默认2个线程
- **下载目录**：`./downloads`
- **解压目录**：`./extracted`

#### 3. 输出结果

**3.1 文件结构**

```
项目目录/
├── downloads/           # 原始.gz文件
│   ├── d07_text_station_5min_2025_03_19.txt.gz
│   └── d04_text_station_5min_2025_03_20.txt.gz
└── extracted/          # 解压后的.txt文件
    ├── d07_text_station_5min_2025_03_19.txt
    └── d04_text_station_5min_2025_03_20.txt
```

**3.2 文件命名规则**

- 保持与浏览器直接下载完全一致的文件名
- 下载文件：`d07_text_station_5min_2025_03_19.txt.gz`
- 解压文件：`d07_text_station_5min_2025_03_19.txt`

**3.3 运行日志示例**

```
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
```

#### 4. 使用方法

1. 配置PeMS网站Cookie
2. 确保代理(如Clash)正常运行
3. 运行脚本
4. 等待自动下载和解压完成

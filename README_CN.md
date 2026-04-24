# qbitclient

qBittorrent API 命令行客户端，支持通过命令行管理 qBittorrent 种子任务。

## 功能特性

- ✅ 添加种子（支持 magnet 链接、torrent 文件 URL、本地 torrent 文件）
- ✅ 列出种子任务（支持过滤、排序、分页）
- ✅ 删除种子任务（可选是否删除下载文件）
- ✅ 环境变量配置支持
- ✅ 详细的任务信息展示

## 环境要求

- Python 3.6+
- requests 库

安装依赖：
```bash
pip install requests
```

## 快速开始

### 1. 配置连接信息

**方式1：环境变量（推荐）**
```bash
export QBITTORRENT_HOST="http://localhost:8080"
export QBITTORRENT_USERNAME="admin"
export QBITTORRENT_PASSWORD="adminadmin"
```

**方式2：命令行参数**
```bash
python3 qbitclient.py --host http://localhost:8080 --username admin --password adminadmin list
```

### 2. 基本使用

```bash
# 列出所有种子
python3 qbitclient.py list

# 添加 magnet 链接
python3 qbitclient.py add-url "magnet:?xt=urn:btih:..."

# 添加本地 torrent 文件
python3 qbitclient.py add-file "/path/to/file.torrent"

# 删除种子
python3 qbitclient.py rm HASH_VALUE
```

## 命令详解

### add-url - 添加种子 URL

支持 magnet 链接和 torrent 文件 URL。

```bash
python3 qbitclient.py add-url URL [URL ...] [选项]

选项：
  --category 分类名称
  --tags 标签（逗号分隔）
  --save-path 保存路径
  --paused 暂停添加
```

示例：
```bash
# 添加一个 magnet 链接
python3 qbitclient.py add-url "magnet:?xt=urn:btih:..."

# 添加多个 URL
python3 qbitclient.py add-url "magnet:?xt=..." "http://example.com/file.torrent"

# 添加并指定分类
python3 qbitclient.py add-url "magnet:?xt=..." --category movies --tags hd,1080p
```

### add-file - 添加本地 torrent 文件

```bash
python3 qbitclient.py add-file FILE [FILE ...] [选项]

选项：
  --category 分类名称
  --tags 标签（逗号分隔）
  --save-path 保存路径
  --paused 暂停添加
```

示例：
```bash
# 添加一个 torrent 文件
python3 qbitclient.py add-file "/path/to/file.torrent"

# 添加多个 torrent 文件
python3 qbitclient.py add-file file1.torrent file2.torrent --category tv
```

### list - 列出种子任务

```bash
python3 qbitclient.py list [选项]

选项：
  --filter 过滤状态（all/downloading/seeding/completed/paused/active/inactive等）
  --category 按分类过滤
  --tag 按标签过滤
  --sort 排序字段
  --reverse 反向排序
  --limit 限制返回数量
  -v, --verbose 显示详细信息
```

示例：
```bash
# 列出所有种子
python3 qbitclient.py list

# 列出正在下载的种子
python3 qbitclient.py list --filter downloading

# 详细模式
python3 qbitclient.py list -v

# 按分类过滤
python3 qbitclient.py list --category movies

# 限制返回数量
python3 qbitclient.py list --limit 10 --sort progress --reverse
```

### rm - 删除种子任务

```bash
python3 qbitclient.py rm HASH [HASH ...] [选项]

选项：
  --delete-files 同时删除下载的文件
```

示例：
```bash
# 删除单个种子（保留文件）
python3 qbitclient.py rm 8c212779b4abde7c6bc608063a0d008b7e40ce32

# 删除多个种子
python3 qbitclient.py rm HASH1 HASH2 HASH3

# 删除种子及文件
python3 qbitclient.py rm HASH --delete-files

# 删除所有种子
python3 qbitclient.py rm all
```

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `QBITTORRENT_HOST` | qBittorrent WebUI 地址 | `http://localhost:8080` |
| `QBITTORRENT_USERNAME` | 用户名 | `admin` |
| `QBITTORRENT_PASSWORD` | 密码 | `adminadmin` |

优先级：命令行参数 > 环境变量 > 默认值

## 输出格式

### 简洁模式（默认）
```
==================================================

名称: Ubuntu 22.04 LTS
  Hash: 8c212779b4abde7c6bc608063a0d008b7e40ce32
  状态: downloading
  大小: 3.52 GB
  进度: 45.3%
==================================================
```

### 详细模式（-v）
```
==================================================

名称: Ubuntu 22.04 LTS
  Hash: 8c212779b4abde7c6bc608063a0d008b7e40ce32
  状态: downloading
  大小: 3.52 GB
  进度: 45.3%
  下载速度: 5.23 MB/s
  上传速度: 1.12 MB/s
  已下载: 1.59 GB
  已上传: 356.82 MB
  分享率: 0.21
  ETA: 542 秒
  分类: linux
  标签: iso,ubuntu
==================================================
```

## qBittorrent API 版本

本脚本兼容 qBittorrent v4.1+ 的 WebUI API。

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 作者

Generated with CodeBuddy Code

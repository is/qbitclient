#!/usr/bin/env python3
"""
qBittorrent API Client
支持添加种子、列出任务和删除任务
使用Python内置urllib，无需外部依赖
"""

import sys
import json
import argparse
import os
import http.cookiejar
from pathlib import Path
from urllib import request, parse, error


# 环境变量名称
ENV_HOST = 'QBITTORRENT_HOST'
ENV_USERNAME = 'QBITTORRENT_USERNAME'
ENV_PASSWORD = 'QBITTORRENT_PASSWORD'


class SimpleSession:
    """简单的HTTP会话类，使用urllib实现，支持Cookie"""
    
    def __init__(self):
        self.cookie_jar = http.cookiejar.CookieJar()
        self.opener = request.build_opener(
            request.HTTPCookieProcessor(self.cookie_jar)
        )
    
    def post(self, url, data=None, headers=None, timeout=10, files=None):
        """发送POST请求"""
        if files:
            # multipart/form-data 上传
            return self._post_multipart(url, data, files, headers, timeout)
        else:
            # application/x-www-form-urlencoded
            req_headers = headers or {}
            if data:
                encoded_data = parse.urlencode(data).encode('utf-8')
            else:
                encoded_data = None
            
            req = request.Request(url, data=encoded_data, headers=req_headers, method='POST')
            return self._do_request(req, timeout)
    
    def get(self, url, params=None, headers=None, timeout=10):
        """发送GET请求"""
        req_headers = headers or {}
        
        if params:
            url = url + '?' + parse.urlencode(params)
        
        req = request.Request(url, headers=req_headers, method='GET')
        return self._do_request(req, timeout)
    
    def _do_request(self, req, timeout):
        """执行请求并返回响应对象"""
        try:
            response = self.opener.open(req, timeout=timeout)
            return SimpleResponse(response)
        except error.HTTPError as e:
            return SimpleResponse(e)
        except error.URLError as e:
            raise Exception(f"连接错误: {str(e)}")
    
    def _post_multipart(self, url, data, files, headers=None, timeout=30):
        """处理multipart/form-data上传"""
        boundary = b'----FormBoundary' + os.urandom(8).hex().encode()
        body_parts = []
        
        # 添加表单字段
        if data:
            for key, value in data.items():
                body_parts.append(b'--' + boundary)
                body_parts.append(f'Content-Disposition: form-data; name="{key}"'.encode())
                body_parts.append(b'')
                body_parts.append(str(value).encode())
        
        # 添加文件
        for field_name, (filename, file_data, content_type) in files.items():
            body_parts.append(b'--' + boundary)
            body_parts.append(f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"'.encode())
            body_parts.append(f'Content-Type: {content_type}'.encode())
            body_parts.append(b'')
            body_parts.append(file_data)
        
        body_parts.append(b'--' + boundary + b'--')
        body_parts.append(b'')
        
        body = b'\r\n'.join(body_parts)
        
        req_headers = headers or {}
        req_headers['Content-Type'] = f'multipart/form-data; boundary={boundary.decode()}'
        req_headers['Content-Length'] = str(len(body))
        
        req = request.Request(url, data=body, headers=req_headers, method='POST')
        return self._do_request(req, timeout)


class SimpleResponse:
    """简单的响应包装类"""
    
    def __init__(self, response):
        self.status_code = response.getcode() or response.code
        self.headers = dict(response.headers)
        self._response = response
        self._text = None
    
    @property
    def text(self):
        if self._text is None:
            self._text = self._response.read().decode('utf-8', errors='ignore')
        return self._text
    
    def json(self):
        return json.loads(self.text)


class QBittorrentClient:
    def __init__(self, host="http://localhost:8080", username="admin", password="adminadmin"):
        self.host = host.rstrip('/')
        self.username = username
        self.password = password
        self.session = SimpleSession()
        self.logged_in = False

    def login(self):
        """登录qBittorrent"""
        url = f"{self.host}/api/v2/auth/login"
        data = {
            'username': self.username,
            'password': self.password
        }
        headers = {'Referer': self.host}

        try:
            response = self.session.post(url, data=data, headers=headers, timeout=10)
            if response.status_code == 200 and "Ok" in response.text:
                self.logged_in = True
                return True, "登录成功"
            else:
                return False, f"登录失败: {response.text}"
        except Exception as e:
            return False, f"登录错误: {str(e)}"

    def logout(self):
        """登出"""
        if not self.logged_in:
            return

        url = f"{self.host}/api/v2/auth/logout"
        try:
            self.session.post(url, timeout=10)
        except:
            pass
        self.logged_in = False

    def add_torrent_url(self, urls, category=None, tags=None, save_path=None, paused=False):
        """
        添加种子URL（支持magnet链接和torrent文件URL）
        urls: URL列表或单个URL字符串
        """
        if not self.logged_in:
            return False, "未登录"

        url = f"{self.host}/api/v2/torrents/add"

        if isinstance(urls, str):
            urls = [urls]

        data = {
            'urls': '\n'.join(urls)
        }

        if category:
            data['category'] = category
        if tags:
            data['tags'] = tags if isinstance(tags, str) else ','.join(tags)
        if save_path:
            data['savepath'] = save_path
        if paused:
            data['paused'] = 'true'

        try:
            response = self.session.post(url, data=data, timeout=30)
            if response.status_code == 200:
                return True, "种子添加成功"
            else:
                return False, f"添加失败: HTTP {response.status_code}"
        except Exception as e:
            return False, f"添加错误: {str(e)}"

    def add_torrent_file(self, file_paths, category=None, tags=None, save_path=None, paused=False):
        """
        添加本地torrent文件
        file_paths: 文件路径列表或单个文件路径
        """
        if not self.logged_in:
            return False, "未登录"

        url = f"{self.host}/api/v2/torrents/add"

        if isinstance(file_paths, str):
            file_paths = [file_paths]

        files = {}
        for i, file_path in enumerate(file_paths):
            path = Path(file_path)
            if not path.exists():
                return False, f"文件不存在: {file_path}"

            with open(path, 'rb') as f:
                files[f'torrents'] = (path.name, f.read(), 'application/x-bittorrent')

        data = {}
        if category:
            data['category'] = category
        if tags:
            data['tags'] = tags if isinstance(tags, str) else ','.join(tags)
        if save_path:
            data['savepath'] = save_path
        if paused:
            data['paused'] = 'true'

        try:
            response = self.session.post(url, data=data, files=files, timeout=30)
            if response.status_code == 200:
                return True, "种子文件添加成功"
            else:
                return False, f"添加失败: HTTP {response.status_code}"
        except Exception as e:
            return False, f"添加错误: {str(e)}"

    def list_torrents(self, filter_status=None, category=None, tag=None, sort=None, reverse=False, limit=None, offset=None):
        """
        列出所有种子任务
        filter_status: all, downloading, seeding, completed, paused, active, inactive, resumed, stalled等
        """
        if not self.logged_in:
            return None, "未登录"

        url = f"{self.host}/api/v2/torrents/info"
        params = {}

        if filter_status:
            params['filter'] = filter_status
        if category:
            params['category'] = category
        if tag:
            params['tag'] = tag
        if sort:
            params['sort'] = sort
        if reverse:
            params['reverse'] = 'true'
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset

        try:
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                torrents = response.json()
                return True, torrents
            else:
                return False, f"获取列表失败: HTTP {response.status_code}"
        except Exception as e:
            return False, f"获取列表错误: {str(e)}"

    def delete_torrents(self, hashes, delete_files=False):
        """
        删除种子任务
        hashes: 种子hash列表或单个hash，也可以是'all'
        delete_files: 是否同时删除下载的文件
        """
        if not self.logged_in:
            return False, "未登录"

        url = f"{self.host}/api/v2/torrents/delete"

        if isinstance(hashes, list):
            hashes = '|'.join(hashes)

        data = {
            'hashes': hashes,
            'deleteFiles': 'true' if delete_files else 'false'
        }

        try:
            response = self.session.post(url, data=data, timeout=10)
            if response.status_code == 200:
                return True, "删除成功"
            else:
                return False, f"删除失败: HTTP {response.status_code}"
        except Exception as e:
            return False, f"删除错误: {str(e)}"

    def cleanup_completed(self, delete_files=False):
        """
        自动移除已完成的种子任务（进度100%）
        delete_files: 是否同时删除下载的文件
        返回: (success, message, removed_count)
        """
        if not self.logged_in:
            return False, "未登录", 0

        # 获取所有种子
        success, torrents = self.list_torrents()
        if not success:
            return False, f"获取种子列表失败: {torrents}", 0

        # 筛选进度为100%的种子
        completed = [t for t in torrents if t.get('progress', 0) >= 1.0]

        if not completed:
            return True, "没有已完成的种子需要清理", 0

        # 提取hash
        hashes = [t.get('hash') for t in completed if t.get('hash')]

        if not hashes:
            return True, "没有找到有效的种子hash", 0

        # 删除种子
        success, message = self.delete_torrents(hashes, delete_files)
        
        if success:
            return True, f"成功清理 {len(hashes)} 个已完成的种子", len(hashes)
        else:
            return False, message, 0

    def print_torrents(self, torrents, verbose=False):
        """格式化打印种子列表"""
        if not torrents:
            print("没有找到种子任务")
            return

        print(f"\n{'='*100}")
        print(f"共 {len(torrents)} 个种子任务")
        print(f"{'='*100}")

        for t in torrents:
            print(f"\n名称: {t.get('name', 'N/A')}")
            print(f"  Hash: {t.get('hash', 'N/A')}")
            print(f"  状态: {t.get('state', 'N/A')}")
            print(f"  大小: {self._format_size(t.get('size', 0))}")
            print(f"  进度: {t.get('progress', 0)*100:.1f}%")

            if verbose:
                print(f"  下载速度: {self._format_speed(t.get('dlspeed', 0))}")
                print(f"  上传速度: {self._format_speed(t.get('upspeed', 0))}")
                print(f"  已下载: {self._format_size(t.get('downloaded', 0))}")
                print(f"  已上传: {self._format_size(t.get('uploaded', 0))}")
                print(f"  分享率: {t.get('ratio', 0):.2f}")
                print(f"  ETA: {t.get('eta', 0)} 秒")
                if t.get('category'):
                    print(f"  分类: {t.get('category')}")
                if t.get('tags'):
                    print(f"  标签: {t.get('tags')}")

        print(f"\n{'='*100}\n")

    def _format_size(self, size_bytes):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"

    def _format_speed(self, speed_bytes):
        """格式化速度"""
        return f"{self._format_size(speed_bytes)}/s"


def main():
    parser = argparse.ArgumentParser(
        description='qBittorrent API 客户端',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 添加magnet链接
  %(prog)s add-url "magnet:?xt=urn:btih:..."

  # 添加torrent文件URL
  %(prog)s add-url "http://example.com/file.torrent"

  # 添加本地torrent文件
  %(prog)s add-file "/path/to/file.torrent"

  # 列出所有种子
  %(prog)s list

  # 列出正在下载的种子
  %(prog)s list --filter downloading

  # 删除种子（保留文件）
  %(prog)s rm HASH

  # 删除种子（同时删除文件）
  %(prog)s rm HASH --delete-files

环境变量:
  可以通过环境变量设置默认参数:
  export QBITTORRENT_HOST="http://192.168.1.100:8080"
  export QBITTORRENT_USERNAME="admin"
  export QBITTORRENT_PASSWORD="mypassword"

  使用环境变量后，可以简化命令:
  %(prog)s list  # 无需每次指定--host, --username, --password
        """
    )

    parser.add_argument('--host',
                        default=os.getenv(ENV_HOST, 'http://localhost:8080'),
                        help=f'qBittorrent地址 (默认: http://localhost:8080, 可从{ENV_HOST}环境变量读取)')
    parser.add_argument('--username',
                        default=os.getenv(ENV_USERNAME, 'admin'),
                        help=f'用户名 (默认: admin, 可从{ENV_USERNAME}环境变量读取)')
    parser.add_argument('--password',
                        default=os.getenv(ENV_PASSWORD, 'adminadmin'),
                        help=f'密码 (默认: adminadmin, 可从{ENV_PASSWORD}环境变量读取)')

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # add-url 命令
    add_url_parser = subparsers.add_parser('add-url', help='添加种子URL')
    add_url_parser.add_argument('urls', nargs='+', help='种子URL或magnet链接')
    add_url_parser.add_argument('--category', help='分类')
    add_url_parser.add_argument('--tags', help='标签（逗号分隔）')
    add_url_parser.add_argument('--save-path', help='保存路径')
    add_url_parser.add_argument('--paused', action='store_true', help='暂停添加')

    # add-file 命令
    add_file_parser = subparsers.add_parser('add-file', help='添加本地torrent文件')
    add_file_parser.add_argument('files', nargs='+', help='torrent文件路径')
    add_file_parser.add_argument('--category', help='分类')
    add_file_parser.add_argument('--tags', help='标签（逗号分隔）')
    add_file_parser.add_argument('--save-path', help='保存路径')
    add_file_parser.add_argument('--paused', action='store_true', help='暂停添加')

    # list 命令
    list_parser = subparsers.add_parser('list', help='列出种子任务')
    list_parser.add_argument('--filter', help='过滤状态 (all/downloading/seeding/completed/paused/active等)')
    list_parser.add_argument('--category', help='按分类过滤')
    list_parser.add_argument('--tag', help='按标签过滤')
    list_parser.add_argument('--sort', help='排序字段')
    list_parser.add_argument('--reverse', action='store_true', help='反向排序')
    list_parser.add_argument('--limit', type=int, help='限制返回数量')
    list_parser.add_argument('-v', '--verbose', action='store_true', help='显示详细信息')

    # rm 命令
    rm_parser = subparsers.add_parser('rm', help='删除种子任务')
    rm_parser.add_argument('hashes', nargs='+', help='种子hash或"all"')
    rm_parser.add_argument('--delete-files', action='store_true', help='同时删除下载的文件')

    # cleanup 命令
    cleanup_parser = subparsers.add_parser('cleanup', help='自动移除已完成的种子(进度100%%)')
    cleanup_parser.add_argument('--delete-files', action='store_true', help='同时删除下载的文件')
    cleanup_parser.add_argument('--dry-run', action='store_true', help='仅列出已完成的种子，不执行删除')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # 创建客户端
    client = QBittorrentClient(
        host=args.host,
        username=args.username,
        password=args.password
    )

    # 登录
    success, message = client.login()
    if not success:
        print(f"错误: {message}")
        sys.exit(1)

    print(f"✓ {message}")

    try:
        if args.command == 'add-url':
            success, message = client.add_torrent_url(
                urls=args.urls,
                category=args.category,
                tags=args.tags,
                save_path=args.save_path,
                paused=args.paused
            )
            print(f"{'✓' if success else '✗'} {message}")

        elif args.command == 'add-file':
            success, message = client.add_torrent_file(
                file_paths=args.files,
                category=args.category,
                tags=args.tags,
                save_path=args.save_path,
                paused=args.paused
            )
            print(f"{'✓' if success else '✗'} {message}")

        elif args.command == 'list':
            success, result = client.list_torrents(
                filter_status=args.filter,
                category=args.category,
                tag=args.tag,
                sort=args.sort,
                reverse=args.reverse,
                limit=args.limit
            )

            if success:
                client.print_torrents(result, verbose=args.verbose)
            else:
                print(f"✗ {result}")

        elif args.command == 'rm':
            hashes = args.hashes
            if len(hashes) == 1 and hashes[0] == 'all':
                confirm = input("确定要删除所有种子吗? (yes/no): ")
                if confirm.lower() != 'yes':
                    print("取消删除")
                    sys.exit(0)
                hashes = 'all'

            success, message = client.delete_torrents(
                hashes=hashes,
                delete_files=args.delete_files
            )
            print(f"{'✓' if success else '✗'} {message}")

        elif args.command == 'cleanup':
            # 获取已完成的种子
            success, torrents_result = client.list_torrents()

            if not success:
                print(f"✗ 获取种子列表失败: {torrents_result}")
                sys.exit(1)

            # 筛选进度为100%的种子
            completed = [t for t in torrents_result if t.get('progress', 0) >= 1.0]

            if not completed:
                print("✓ 没有已完成的种子需要清理")
                sys.exit(0)

            # 显示已完成的种子
            print(f"\n找到 {len(completed)} 个已完成的种子:")
            client.print_torrents(completed, verbose=False)

            if args.dry_run:
                print("✓ Dry run 模式，未执行删除")
                sys.exit(0)

            # 确认删除
            confirm = input(f"确定要删除这 {len(completed)} 个已完成的种子吗? (yes/no): ")
            if confirm.lower() != 'yes':
                print("取消删除")
                sys.exit(0)

            # 提取hash并删除
            hashes = [t.get('hash') for t in completed if t.get('hash')]

            success, message = client.delete_torrents(
                hashes=hashes,
                delete_files=args.delete_files
            )
            print(f"{'✓' if success else '✗'} {message}")

    finally:
        client.logout()


if __name__ == '__main__':
    main()

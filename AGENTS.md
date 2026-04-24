# AGENTS.md - AI Agent Context

本项目是一个 qBittorrent API 命令行客户端，用于通过命令行管理 qBittorrent 种子任务。

## 项目结构

```
/is/qbit/
├── qbitclient.py    # 主程序，qBittorrent API 客户端
├── README.md        # 用户文档
└── AGENTS.md        # AI Agent 上下文（本文件）
```

## 代码架构

### qbitclient.py

**核心类：`QBittorrentClient`**

封装了 qBittorrent WebUI API 的所有操作：

- `__init__(host, username, password)` - 初始化客户端
- `login()` / `logout()` - 登录/登出
- `add_torrent_url(urls, ...)` - 添加种子 URL
- `add_torrent_file(files, ...)` - 添加本地 torrent 文件
- `list_torrents(...)` - 列出种子任务
- `delete_torrents(hashes, ...)` - 删除种子任务
- `print_torrents(torrents, verbose)` - 格式化输出

**配置优先级：**
1. 命令行参数（最高优先级）
2. 环境变量
3. 默认值（最低优先级）

**环境变量支持：**
- `QBITTORRENT_HOST` - qBittorrent 地址
- `QBITTORRENT_USERNAME` - 用户名
- `QBITTORRENT_PASSWORD` - 密码

## 关键设计决策

1. **使用 `requests.Session()`** - 自动处理 cookie，保持登录状态
2. **统一的返回值格式** - 所有 API 方法返回 `(success: bool, message/data)` 元组
3. **支持批量操作** - `add_torrent_*` 和 `delete_torrents` 都支持列表输入
4. **安全的删除确认** - 删除 `all` 时需要用户确认
5. **简洁/详细双模式输出** - `list` 命令支持 `-v` 详细模式

## qBittorrent API 要点

- **认证方式：** Cookie-based，登录后所有请求需携带 SID cookie
- **API 路径：** `/api/v2/{APIName}/{methodName}`
- **添加种子：** `POST /api/v2/torrents/add`，支持 `urls` 参数或 `torrents` 文件上传
- **列出种子：** `GET /api/v2/torrents/info`，支持过滤、排序、分页
- **删除种子：** `POST /api/v2/torrents/delete`，`hashes` 参数支持 `|` 分隔多个 hash
- **Hash 分隔符：** 多个 hash 用 `|` 分隔（不是逗号）

## 常见任务

### 添加新功能

1. 在 `QBittorrentClient` 类中添加新方法
2. 在 `main()` 中添加对应的 subparser
3. 更新 README.md 添加使用示例

### 调试 API 问题

```bash
# 启用详细日志
python3 -c "
import requests
import logging
logging.basicConfig(level=logging.DEBUG)
# 测试代码
"
```

### 测试连接

```bash
# 测试登录
python3 qbitclient.py list

# 如果失败，检查：
# 1. qBittorrent 是否运行
# 2. WebUI 是否启用（工具 -> 选项 -> Web UI）
# 3. 主机、端口、用户名、密码是否正确
```

## 依赖

- Python 3.6+
- requests (HTTP 库)

安装：`pip install requests`

## 注意事项

1. **Referer 头** - qBittorrent API 需要设置 `Referer: http://host:port`，否则可能返回 403
2. **布尔参数格式** - 某些 API 使用字符串 `"true"`/`"false"`，某些使用布尔值，需查阅文档
3. **文件路径分隔符** - API 使用 `/` 作为路径分隔符（即使 Windows）
4. **URL 编码** - 分类名、标签等含空格的参数需要 URL 编码

## 扩展建议

如需扩展功能，可添加：

- [ ] 种子暂停/恢复
- [ ] 修改种子分类/标签
- [ ] 设置分享率限制
- [ ] 查看/管理分类
- [ ] 查看/管理标签
- [ ] 查看传输信息（速度、流量统计）
- [ ] 配置文件支持（JSON/YAML）
- [ ] 交互式模式（类似 ncurses）
- [ ] 输出格式选项（JSON/表格/简洁）

## 相关文档

- [qBittorrent WebUI API 文档](https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1))
- [qbittorrent-api Python 库](https://qbittorrent-api.readthedocs.io/)（如需要更高级功能可参考）

## 维护者注意事项

- 保持向后兼容性，不要破坏现有命令行接口
- 添加新的命令行参数时，同时添加对应的环境变量支持
- 更新功能时同步更新 README.md
- 遵循 PEP 8 代码风格

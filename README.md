# qbitclient

A command-line client for qBittorrent API, allowing you to manage qBittorrent torrent tasks via the command line.

## Features

- ✅ Add torrents (supports magnet links, torrent file URLs, and local torrent files)
- ✅ List torrent tasks (supports filtering, sorting, and pagination)
- ✅ Delete torrent tasks (optional file deletion)
- ✅ Environment variable configuration support
- ✅ Detailed task information display

## Requirements

- Python 3.6+
- requests library

Install dependencies:
```bash
pip install requests
```

## Quick Start

### 1. Configure Connection

**Option 1: Environment Variables (Recommended)**
```bash
export QBITTORRENT_HOST="http://localhost:8080"
export QBITTORRENT_USERNAME="admin"
export QBITTORRENT_PASSWORD="adminadmin"
```

**Option 2: Command-line Arguments**
```bash
python3 qbitclient.py --host http://localhost:8080 --username admin --password adminadmin list
```

### 2. Basic Usage

```bash
# List all torrents
python3 qbitclient.py list

# Add a magnet link
python3 qbitclient.py add-url "magnet:?xt=urn:btih:..."

# Add a local torrent file
python3 qbitclient.py add-file "/path/to/file.torrent"

# Delete a torrent
python3 qbitclient.py rm HASH_VALUE
```

## Command Reference

### add-url - Add Torrent URL

Supports magnet links and torrent file URLs.

```bash
python3 qbitclient.py add-url URL [URL ...] [OPTIONS]

Options:
  --category CATEGORY    Category name
  --tags TAGS            Tags (comma-separated)
  --save-path PATH       Save path
  --paused               Add in paused state
```

Examples:
```bash
# Add a magnet link
python3 qbitclient.py add-url "magnet:?xt=urn:btih:..."

# Add multiple URLs
python3 qbitclient.py add-url "magnet:?xt=..." "http://example.com/file.torrent"

# Add with category and tags
python3 qbitclient.py add-url "magnet:?xt=..." --category movies --tags hd,1080p
```

### add-file - Add Local Torrent File

```bash
python3 qbitclient.py add-file FILE [FILE ...] [OPTIONS]

Options:
  --category CATEGORY    Category name
  --tags TAGS            Tags (comma-separated)
  --save-path PATH       Save path
  --paused               Add in paused state
```

Examples:
```bash
# Add a torrent file
python3 qbitclient.py add-file "/path/to/file.torrent"

# Add multiple torrent files
python3 qbitclient.py add-file file1.torrent file2.torrent --category tv
```

### list - List Torrent Tasks

```bash
python3 qbitclient.py list [OPTIONS]

Options:
  --filter FILTER        Filter by status (all/downloading/seeding/completed/paused/active/inactive, etc.)
  --category CATEGORY    Filter by category
  --tag TAG              Filter by tag
  --sort FIELD           Sort field (name/size/progress/added_on/completion_on/ratio, etc.)
  --reverse              Reverse sort order
  --limit NUM            Limit number of results
  -v, --verbose         Show detailed information
```

Examples:
```bash
# List all torrents
python3 qbitclient.py list

# List downloading torrents
python3 qbitclient.py list --filter downloading

# Verbose mode
python3 qbitclient.py list -v

# Filter by category
python3 qbitclient.py list --category movies

# Sort by addition date (oldest first)
python3 qbitclient.py list --sort added_on

# Sort by addition date (newest first)
python3 qbitclient.py list --sort added_on --reverse

# Sort by completion date
python3 qbitclient.py list --sort completion_on

# Limit results
python3 qbitclient.py list --limit 10 --sort progress --reverse
```

### rm - Delete Torrent Tasks

```bash
python3 qbitclient.py rm HASH [HASH ...] [OPTIONS]

Options:
  --delete-files         Also delete downloaded files
```

Examples:
```bash
# Delete a single torrent (keep files)
python3 qbitclient.py rm 8c212779b4abde7c6bc608063a0d008b7e40ce32

# Delete multiple torrents
python3 qbitclient.py rm HASH1 HASH2 HASH3

# Delete torrent and files
python3 qbitclient.py rm HASH --delete-files

# Delete all torrents
python3 qbitclient.py rm all
```

### cleanup - Cleanup Completed Torrents

Automatically remove completed torrents (progress = 100%).

```bash
python3 qbitclient.py cleanup [OPTIONS]

Options:
  --delete-files         Also delete downloaded files
  --dry-run              List completed torrents without deleting
  -y, --yes              Skip confirmation prompt and delete directly
```

Examples:
```bash
# Cleanup completed torrents (with confirmation)
python3 qbitclient.py cleanup

# Cleanup and delete files
python3 qbitclient.py cleanup --delete-files

# Dry run - list without deleting
python3 qbitclient.py cleanup --dry-run

# Skip confirmation
python3 qbitclient.py cleanup --yes
python3 qbitclient.py cleanup -y
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `QBITTORRENT_HOST` | qBittorrent WebUI address | `http://localhost:8080` |
| `QBITTORRENT_USERNAME` | Username | `admin` |
| `QBITTORRENT_PASSWORD` | Password | `adminadmin` |

Priority: Command-line arguments > Environment variables > Default values

## Output Format

### Concise Mode (Default)
```
==================================================

Name: Ubuntu 22.04 LTS
  Hash: 8c212779b4abde7c6bc608063a0d008b7e40ce32
  State: downloading
  Size: 3.52 GB
  Progress: 45.3%
==================================================
```

### Verbose Mode (-v)
```
==================================================

Name: Ubuntu 22.04 LTS
  Hash: 8c212779b4abde7c6bc608063a0d008b7e40ce32
  State: downloading
  Size: 3.52 GB
  Progress: 45.3%
  Download Speed: 5.23 MB/s
  Upload Speed: 1.12 MB/s
  Downloaded: 1.59 GB
  Uploaded: 356.82 MB
  Ratio: 0.21
  ETA: 542 seconds
  Category: linux
  Tags: iso,ubuntu
==================================================
```

## qBittorrent API Version

This script is compatible with qBittorrent v4.1+ WebUI API.

## License

MIT License

## Contributing

Issues and Pull Requests are welcome!

## Author

Generated with CodeBuddy Code

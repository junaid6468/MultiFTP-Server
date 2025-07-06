# 🚀 MultiFTP-Server

A lightweight, multithreaded FTP server written in Python. This project enables users to connect via FTP and perform file operations such as uploading, downloading, listing files, and changing directories. It uses Python's `socket` and `threading` libraries to manage concurrent client sessions and supports passive mode data transfer.

---

## 🧠 Features

- 🔁 **Multithreaded Design** — Handles multiple clients simultaneously using Python threads
- 📂 **Directory Navigation** — Commands like `PWD`, `CWD`, and `CDUP` for path management
- 📋 **List Files (LIST)** — View server files and directories in a formatted table
- ⬇️ **Download (RETR)** — Download files from the server
- ⬆️ **Upload (STOR)** — Upload files to the server
- 🧱 **Basic Command Handling** — Supports fundamental FTP commands
- 📄 **Simple Logging** — Console logs for incoming connections and actions

---

## 🛠️ Technologies Used

- Python 3.x
- `socket` — For TCP-based server-client communication
- `threading` — To handle concurrent clients
- `os`, `time`, `sys` — File handling and formatting utilities

---

## 📦 Installation & Setup

### 🔧 Prerequisites

- Python 3.6+
- Basic understanding of the command line

### 🚀 Running the Server

```bash
python server.py
python client.py

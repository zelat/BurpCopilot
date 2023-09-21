#!/usr/bin/env python
# -*- coding: utf-8 -*-
from java.io import File, FileWriter
from java.util import UUID

class Logger:
    def __init__(self):
        unique_filename = str(UUID.randomUUID()) + ".txt"  # 生成一个唯一的文件名
        self.log_file_path = "C:\\CodeRepository\\BurpCopilot\\log\\" + unique_filename
        self._ensure_file_exists()  # 确保文件存在

    def _ensure_file_exists(self):
        file = File(self.log_file_path)
        if not file.exists():
            file.getParentFile().mkdirs() # 创建所需的目录结构
            file.createNewFile()  # 创建文件

    def _log(self, level, message):
        log_file = FileWriter(self.log_file_path, True)
        log_entry = "[{}] {}: {}\n".format(level, "Logger", message)
        log_file.write(log_entry) # 写入日志条目
        log_file.close() # 关闭文件

    def error(self, message):
        self._log("ERROR", message)

    def warn(self, message):
        self._log("WARN", message)

    def debug(self, message):
        self._log("DEBUG", message)
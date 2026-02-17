#!/usr/bin/env python3
"""
跨平台软件安装解决方案
支持Windows和macOS操作系统
"""

import os
import sys
import platform
import subprocess
import json
import time
import locale
from pathlib import Path

# 尝试导入colorama以支持彩色输出
try:
    from colorama import init, Fore, Back, Style
    init()
    COLOR_SUPPORTED = True
except ImportError:
    COLOR_SUPPORTED = False

# 彩色输出函数
def print_color(text, color=None):
    """打印彩色文本"""
    if COLOR_SUPPORTED and color:
        print(f"{color}{text}{Style.RESET_ALL}")
    else:
        print(text)

# 全局变量
APP_NAME = "SwiftInstall"
APP_VERSION = "1.0.0"

# 配置文件路径
CONFIG_DIR = Path.home() / ".swiftinstall"
CONFIG_FILE = CONFIG_DIR / "config.json"
PROTOCOL_FILE = CONFIG_DIR / "privacy_policy.md"
THIRD_PARTY_FILE = CONFIG_DIR / "third_party.md"

# 支持的语言
SUPPORTED_LANGUAGES = {
    "zh": "中文",
    "en": "English"
}

# 软件源配置
SOFTWARE_SOURCES = {
    "global": {
        "app_url": "https://example.com/app",
        "update_url": "https://example.com/update"
    },
    "china": {
        "app_url": "https://example-cn.com/app",
        "update_url": "https://example-cn.com/update"
    }
}

class Installer:
    def __init__(self):
        """初始化安装器"""
        self.platform = platform.system().lower()
        self.language = None
        self.region = None
        self.source = None
        self.install_dir = None
        self.install_start_time = None
        self.install_end_time = None
        
        # 确保配置目录存在
        CONFIG_DIR.mkdir(exist_ok=True)
        
        # 初始化颜色变量
        if COLOR_SUPPORTED:
            self.COLOR_INFO = Fore.CYAN
            self.COLOR_SUCCESS = Fore.GREEN
            self.COLOR_WARNING = Fore.YELLOW
            self.COLOR_ERROR = Fore.RED
            self.COLOR_RESET = Style.RESET_ALL
        else:
            self.COLOR_INFO = ""
            self.COLOR_SUCCESS = ""
            self.COLOR_WARNING = ""
            self.COLOR_ERROR = ""
            self.COLOR_RESET = ""
    
    def detect_platform(self):
        """检测操作系统平台"""
        if self.platform not in ["windows", "darwin"]:
            print_color("错误: 不支持的操作系统。仅支持Windows和macOS。", self.COLOR_ERROR)
            sys.exit(1)
        return self.platform
    
    def detect_language(self):
        """自动检测系统语言"""
        try:
            # 获取系统语言
            system_lang = locale.getdefaultlocale()[0]
            if system_lang:
                lang_code = system_lang.split('_')[0].lower()
                if lang_code in SUPPORTED_LANGUAGES:
                    return lang_code
        except Exception as e:
            print_color(f"检测语言时出错: {e}", self.COLOR_WARNING)
        
        # 默认返回英文
        return "en"
    
    def select_language(self):
        """让用户选择语言"""
        auto_lang = self.detect_language()
        print_color(f"自动检测到的语言: {SUPPORTED_LANGUAGES[auto_lang]}", self.COLOR_INFO)
        
        print_color("可用语言:", self.COLOR_INFO)
        for code, name in SUPPORTED_LANGUAGES.items():
            print(f"  {code}: {name}")
        
        choice = input(f"请选择语言 (默认: {auto_lang}): ").strip()
        if choice and choice in SUPPORTED_LANGUAGES:
            self.language = choice
        else:
            self.language = auto_lang
        
        return self.language
    
    def detect_region(self):
        """检测用户区域"""
        try:
            # 尝试通过IP检测区域
            if self.platform == "windows":
                # Windows平台检测
                pass
            else:
                # macOS平台检测
                result = subprocess.run(
                    ["curl", "-s", "https://ipinfo.io/json"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    country = data.get("country", "").upper()
                    if country == "CN":
                        return "china"
        except Exception as e:
            print_color(f"检测区域时出错: {e}", self.COLOR_WARNING)
            print_color("将默认使用全球软件源", self.COLOR_INFO)
        
        return "global"
    
    def select_source(self):
        """选择软件源"""
        self.region = self.detect_region()
        if self.region == "china":
            print_color("检测到您位于中国大陆，将使用中国大陆软件源", self.COLOR_SUCCESS)
            self.source = SOFTWARE_SOURCES["china"]
        else:
            print_color("将使用全球软件源", self.COLOR_INFO)
            self.source = SOFTWARE_SOURCES["global"]
        
        return self.source
    
    def show_privacy_policy(self):
        """显示隐私协议"""
        print_color("\n===== 隐私协议 =====", self.COLOR_INFO)
        
        # 读取或生成隐私协议
        if PROTOCOL_FILE.exists():
            with open(PROTOCOL_FILE, 'r', encoding='utf-8') as f:
                print(f.read())
        else:
            # 生成默认隐私协议
            policy = """
隐私协议

1. 数据收集与使用
   - 本安装程序仅收集必要的系统信息，用于适配安装流程
   - 我们不会收集任何个人身份信息
   - 所有数据仅用于本地处理，不会上传至任何服务器

2. 第三方组件
   - 本安装程序包含第三方组件，详情请见第三方组件声明

3. 用户权利与选择
   - 您有权选择是否安装本软件
   - 您可以随时卸载本软件

4. 免责声明
   - 本软件按"原样"提供，不提供任何明示或暗示的担保
   - 在法律允许的范围内，作者不对任何直接或间接损害负责
            """
            print(policy)
            # 保存到文件
            with open(PROTOCOL_FILE, 'w', encoding='utf-8') as f:
                f.write(policy)
        
        # 确认协议
        while True:
            confirm = input("\n是否同意隐私协议？ (y/n): ").strip().lower()
            if confirm == 'y':
                return True
            elif confirm == 'n':
                print_color("您必须同意隐私协议才能继续安装。", self.COLOR_ERROR)
                return False
            else:
                print_color("请输入 'y' 或 'n'。", self.COLOR_WARNING)
    
    def show_third_party_notice(self):
        """显示第三方组件声明"""
        print_color("\n===== 第三方组件声明 =====", self.COLOR_INFO)
        
        # 读取或生成第三方组件声明
        if THIRD_PARTY_FILE.exists():
            with open(THIRD_PARTY_FILE, 'r', encoding='utf-8') as f:
                print(f.read())
        else:
            # 生成默认第三方组件声明
            third_party = """
第三方组件声明

本软件包含以下第三方组件：

1. Python
   - 来源: https://www.python.org/
   - 许可证: PSF许可证

2. curl
   - 来源: https://curl.se/
   - 许可证: MIT许可证

3. 其他可能的依赖项
   - 将根据操作系统和安装需求自动安装
            """
            print(third_party)
            # 保存到文件
            with open(THIRD_PARTY_FILE, 'w', encoding='utf-8') as f:
                f.write(third_party)
        
        input("\n按Enter键继续...")
    
    def download_software(self):
        """下载软件"""
        print_color("\n===== 下载软件 =====", self.COLOR_INFO)
        print_color(f"正在从 {self.source['app_url']} 下载...", self.COLOR_INFO)
        
        # 模拟下载过程
        download_start = time.time()
        for i in range(101):
            time.sleep(0.05)
            # 计算下载速度（模拟）
            elapsed = time.time() - download_start
            speed = (i / 100.0) / max(elapsed, 0.1) * 10  # 模拟10MB文件
            sys.stdout.write(f"\r下载进度: {i}% | 速度: {speed:.2f} MB/s")
            sys.stdout.flush()
        print_color("\n下载完成！", self.COLOR_SUCCESS)
    
    def install_software(self):
        """安装软件"""
        print_color("\n===== 安装软件 =====", self.COLOR_INFO)
        
        if self.platform == "windows":
            # Windows安装逻辑
            print_color("正在Windows上安装...", self.COLOR_INFO)
            # 这里添加Windows特定的安装代码
        else:
            # macOS安装逻辑
            print_color("正在macOS上安装...", self.COLOR_INFO)
            # 这里添加macOS特定的安装代码
        
        # 模拟安装过程
        install_start = time.time()
        steps = ["准备安装环境", "解压安装包", "复制文件", "配置系统", "注册服务", "完成安装"]
        step_count = len(steps)
        step_duration = 3.0 / step_count  # 总安装时间约3秒
        
        for i in range(101):
            time.sleep(0.03)
            # 计算当前步骤
            current_step = min(int(i / (100 / step_count)), step_count - 1)
            sys.stdout.write(f"\r安装进度: {i}% | 当前步骤: {steps[current_step]}")
            sys.stdout.flush()
        print_color("\n安装完成！", self.COLOR_SUCCESS)
    
    def start_application(self):
        """启动应用程序"""
        print_color("\n===== 启动应用程序 =====", self.COLOR_INFO)
        
        if self.platform == "windows":
            # Windows启动逻辑
            print_color("正在Windows上启动应用...", self.COLOR_INFO)
            # 这里添加Windows特定的启动代码
        else:
            # macOS启动逻辑
            print_color("正在macOS上启动应用...", self.COLOR_INFO)
            # 这里添加macOS特定的启动代码
        
        # 模拟启动过程
        for i in range(101):
            time.sleep(0.01)
            sys.stdout.write(f"\r启动进度: {i}%")
            sys.stdout.flush()
        print_color("\n应用程序已启动！", self.COLOR_SUCCESS)
    
    def save_config(self):
        """保存配置"""
        config = {
            "platform": self.platform,
            "language": self.language,
            "region": self.region,
            "source": self.source,
            "install_dir": str(self.install_dir),
            "install_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "install_duration": round(self.install_end_time - self.install_start_time, 2) if self.install_start_time and self.install_end_time else None
        }
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def run(self):
        """运行完整的安装流程"""
        try:
            self.install_start_time = time.time()
            
            # 显示欢迎信息
            print_color(f"{APP_NAME} v{APP_VERSION}", self.COLOR_INFO)
            print_color("跨平台软件安装解决方案", self.COLOR_INFO)
            print_color("==============================", self.COLOR_INFO)
            
            # 1. 检测平台
            print_color("\n1. 检测操作系统平台", self.COLOR_INFO)
            self.detect_platform()
            platform_name = "Windows" if self.platform == "windows" else "macOS"
            print_color(f"检测到平台: {platform_name}", self.COLOR_SUCCESS)
            
            # 2. 选择语言
            print_color("\n2. 选择语言", self.COLOR_INFO)
            self.select_language()
            print_color(f"选择的语言: {SUPPORTED_LANGUAGES[self.language]}", self.COLOR_SUCCESS)
            
            # 3. 显示隐私协议
            print_color("\n3. 隐私协议确认", self.COLOR_INFO)
            if not self.show_privacy_policy():
                return False
            
            # 4. 显示第三方组件声明
            print_color("\n4. 第三方组件声明", self.COLOR_INFO)
            self.show_third_party_notice()
            
            # 5. 选择软件源
            print_color("\n5. 选择软件源", self.COLOR_INFO)
            self.select_source()
            source_name = "中国大陆" if self.region == "china" else "全球"
            print_color(f"选择的软件源: {source_name}", self.COLOR_SUCCESS)
            
            # 6. 下载软件
            print_color("\n6. 下载软件", self.COLOR_INFO)
            self.download_software()
            
            # 7. 安装软件
            print_color("\n7. 安装软件", self.COLOR_INFO)
            self.install_software()
            
            # 8. 启动应用程序
            print_color("\n8. 启动应用程序", self.COLOR_INFO)
            self.start_application()
            
            # 9. 保存配置
            self.install_end_time = time.time()
            self.save_config()
            
            # 显示安装总结
            print_color("\n===== 安装总结 =====", self.COLOR_INFO)
            print_color(f"安装时间: {time.strftime('%Y-%m-%d %H:%M:%S')}", self.COLOR_INFO)
            print_color(f"安装平台: {platform_name}", self.COLOR_INFO)
            print_color(f"使用语言: {SUPPORTED_LANGUAGES[self.language]}", self.COLOR_INFO)
            print_color(f"软件源: {source_name}", self.COLOR_INFO)
            if self.install_start_time and self.install_end_time:
                duration = round(self.install_end_time - self.install_start_time, 2)
                print_color(f"安装耗时: {duration} 秒", self.COLOR_INFO)
            print_color("\n🎉 安装完成！", self.COLOR_SUCCESS)
            print_color("感谢您使用 SwiftInstall！", self.COLOR_INFO)
            
            return True
            
        except KeyboardInterrupt:
            print_color("\n\n安装已被用户取消。", self.COLOR_WARNING)
            return False
        except Exception as e:
            print_color(f"\n❌ 安装过程中出错: {e}", self.COLOR_ERROR)
            import traceback
            traceback.print_exc()
            print_color("\n请检查错误信息并尝试重新安装。", self.COLOR_WARNING)
            return False

if __name__ == "__main__":
    installer = Installer()
    installer.run()

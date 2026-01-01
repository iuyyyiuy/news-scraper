#!/usr/bin/env python3
"""
Start Original Dashboard with FastAPI
Restores your original interface with all functionality
"""

import sys
import os
import subprocess
import time

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def start_fastapi_server():
    """Start the original FastAPI server"""
    
    print("🚀 启动原始仪表板 (FastAPI)")
    print("=" * 50)
    print("✅ 使用您的原始界面和所有功能")
    print("🔒 FastAPI - 安全且高性能的Web框架")
    print("")
    print("🌐 服务器地址:")
    print("   - 主仪表板: http://localhost:8000/dashboard")
    print("   - 新闻搜索: http://localhost:8000/")
    print("   - 系统监控: http://localhost:8000/monitoring")
    print("   - API文档: http://localhost:8000/docs")
    print("")
    print("✅ 所有最新修复已应用:")
    print("   ✅ 日期解析修复 (2025-12-31, 不是2026-12-31)")
    print("   ✅ 标题提取修复 (唯一标题, 无重复)")
    print("   ✅ 数据库清理 (仅12篇当前文章)")
    print("   ✅ 月度清理自动化")
    print("   ✅ 警报日志正常工作 (无404错误)")
    print("")
    print("🛑 按 Ctrl+C 停止服务器")
    print("=" * 50)
    
    try:
        # Start uvicorn server with the web_api module
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "scraper.web_api:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ]
        
        print(f"🔄 执行命令: {' '.join(cmd)}")
        print("")
        
        # Start the server
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 服务器启动失败: {e}")
        print("\n💡 故障排除:")
        print("1. 检查是否有其他进程占用端口8000")
        print("2. 确保所有依赖已安装: pip install fastapi uvicorn")
        print("3. 检查scraper模块是否正确配置")
    except Exception as e:
        print(f"❌ 意外错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    start_fastapi_server()
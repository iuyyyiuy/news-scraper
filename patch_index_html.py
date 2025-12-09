#!/usr/bin/env python3
"""
Script to add sidebar navigation to index.html
"""
import os
import re

def patch_index_html():
    """Add sidebar navigation to index.html"""
    
    index_path = "/Users/kabellatsang/PycharmProjects/ai_code/scraper/templates/index.html"
    
    if not os.path.exists(index_path):
        print(f"❌ Error: {index_path} not found")
        return False
    
    # Read the current file
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already patched
    if 'sidebar' in content.lower() and 'nav-item' in content:
        print("⚠️  index.html already has sidebar!")
        return True
    
    # Create backup
    backup_path = index_path + '.backup_before_sidebar'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup created: {backup_path}")
    
    # Add sidebar styles to CSS
    css_additions = """
        /* Sidebar Navigation */
        .page-container {
            display: flex;
            min-height: 100vh;
            background: #f5f7fa;
        }

        .sidebar {
            width: 250px;
            background: #ffffff;
            border-right: 1px solid #e8ecef;
            padding: 20px;
            position: fixed;
            height: 100vh;
            left: 0;
            top: 0;
        }

        .sidebar-title {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 30px;
            color: #1abc9c;
        }

        .nav-item {
            padding: 12px 16px;
            margin-bottom: 8px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 10px;
            color: #2c3e50;
            text-decoration: none;
        }

        .nav-item:hover {
            background: #f8f9fa;
        }

        .nav-item.active {
            background: #e8f8f5;
            color: #1abc9c;
            font-weight: 500;
        }

        .main-wrapper {
            margin-left: 250px;
            flex: 1;
            padding: 40px 20px;
        }
"""
    
    # Insert CSS before </style>
    content = content.replace('</style>', css_additions + '\n    </style>')
    
    # Wrap body content with sidebar
    # Find <body> tag
    body_start = content.find('<body>')
    body_end = content.find('</body>')
    
    if body_start == -1 or body_end == -1:
        print("❌ Could not find <body> tags")
        return False
    
    # Extract body content
    body_content = content[body_start + 6:body_end].strip()
    
    # Create new body with sidebar
    new_body = """<body>
    <div class="page-container">
        <!-- Sidebar -->
        <div class="sidebar">
            <div class="sidebar-title">📊 Crypto News</div>
            <a href="/dashboard" class="nav-item">
                📰 安全事件数据库
            </a>
            <a href="/" class="nav-item active">
                🔍 新闻搜索
            </a>
        </div>

        <!-- Main Content -->
        <div class="main-wrapper">
""" + body_content + """
        </div>
    </div>
</body>"""
    
    # Replace body section
    content = content[:body_start] + new_body + content[body_end + 7:]
    
    # Write the patched file
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Successfully patched {index_path}")
    print(f"📝 Backup saved to {backup_path}")
    
    return True

if __name__ == "__main__":
    print("🔧 Adding sidebar navigation to index.html...\n")
    
    success = patch_index_html()
    
    if success:
        print("\n🎉 Patching complete!")
        print("\nYou can now:")
        print("1. Start the server: cd /Users/kabellatsang/PycharmProjects/ai_code")
        print("2. Run: python -m uvicorn scraper.web_api:app --reload --host 0.0.0.0 --port 8000")
        print("3. Visit http://localhost:8000/ (Scraper)")
        print("4. Visit http://localhost:8000/dashboard (Database)")
    else:
        print("\n❌ Patching failed!")

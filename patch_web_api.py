#!/usr/bin/env python3
"""
Script to automatically patch web_api.py with database integration
"""
import os
import sys

def patch_web_api():
    """Patch the web_api.py file with database integration"""
    
    web_api_path = "/Users/kabellatsang/PycharmProjects/ai_code/scraper/web_api.py"
    
    if not os.path.exists(web_api_path):
        print(f"❌ Error: {web_api_path} not found")
        return False
    
    # Read the current file
    with open(web_api_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already patched
    if 'database_router' in content:
        print("⚠️  web_api.py already patched!")
        return True
    
    # Create backup
    backup_path = web_api_path + '.backup_before_database'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup created: {backup_path}")
    
    # Find insertion points
    lines = content.split('\n')
    new_lines = []
    
    imports_added = False
    static_mount_added = False
    router_added = False
    startup_added = False
    dashboard_route_added = False
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        # Add imports after existing imports
        if not imports_added and line.startswith('from scraper.core.storage import'):
            new_lines.append('')
            new_lines.append('# Database integration imports')
            new_lines.append('from scraper.api.database_routes import router as database_router, init_scheduler')
            new_lines.append('from fastapi.responses import HTMLResponse')
            imports_added = True
            print("✅ Added imports")
        
        # Add static files mount and router after CORS middleware
        if not router_added and 'allow_headers=' in line and 'CORSMiddleware' in '\n'.join(lines[max(0,i-10):i]):
            new_lines.append('')
            new_lines.append('# Mount static files')
            new_lines.append('app.mount("/static", StaticFiles(directory="scraper/static"), name="static")')
            new_lines.append('')
            new_lines.append('# Include database routes')
            new_lines.append('app.include_router(database_router)')
            router_added = True
            print("✅ Added router integration")
        
        # Add startup event after session_manager initialization
        if not startup_added and line.startswith('session_manager = SessionManager'):
            new_lines.append('')
            new_lines.append('# Initialize scheduler on startup')
            new_lines.append('@app.on_event("startup")')
            new_lines.append('async def startup_event():')
            new_lines.append('    """Initialize scheduler on startup"""')
            new_lines.append('    try:')
            new_lines.append('        init_scheduler()')
            new_lines.append('        logger.info("✅ Scheduler initialized successfully")')
            new_lines.append('    except Exception as e:')
            new_lines.append('        logger.error(f"❌ Failed to initialize scheduler: {e}")')
            new_lines.append('')
            startup_added = True
            print("✅ Added startup event")
    
    # Add dashboard route at the end (before if __name__ == "__main__" if it exists)
    if not dashboard_route_added:
        # Find the right place to insert
        insert_index = len(new_lines)
        for i in range(len(new_lines) - 1, -1, -1):
            if new_lines[i].strip().startswith('if __name__'):
                insert_index = i
                break
        
        dashboard_route = [
            '',
            '# Dashboard route',
            '@app.get("/dashboard", response_class=HTMLResponse)',
            'async def dashboard():',
            '    """Serve the dashboard page"""',
            '    try:',
            '        with open("scraper/templates/dashboard.html", "r", encoding="utf-8") as f:',
            '            html_content = f.read()',
            '        return HTMLResponse(content=html_content)',
            '    except FileNotFoundError:',
            '        raise HTTPException(status_code=404, detail="Dashboard template not found")',
            ''
        ]
        
        new_lines = new_lines[:insert_index] + dashboard_route + new_lines[insert_index:]
        dashboard_route_added = True
        print("✅ Added dashboard route")
    
    # Write the patched file
    with open(web_api_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print(f"\n✅ Successfully patched {web_api_path}")
    print(f"📝 Backup saved to {backup_path}")
    
    return True

if __name__ == "__main__":
    print("🔧 Patching web_api.py with database integration...\n")
    
    success = patch_web_api()
    
    if success:
        print("\n🎉 Patching complete!")
        print("\nNext steps:")
        print("1. Update index.html with sidebar navigation")
        print("2. Start the server: python -m uvicorn scraper.web_api:app --reload")
        print("3. Visit http://localhost:8000/dashboard")
    else:
        print("\n❌ Patching failed!")
        sys.exit(1)

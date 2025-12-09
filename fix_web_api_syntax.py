#!/usr/bin/env python3
"""
Fix syntax error in web_api.py
"""

web_api_path = "/Users/kabellatsang/PycharmProjects/ai_code/scraper/web_api.py"

# Read file
with open(web_api_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the syntax error - add missing closing parenthesis for CORS middleware
content = content.replace(
    '''    allow_headers=["*"],

# Mount static files
app.mount("/static", StaticFiles(directory="scraper/static"), name="static")

# Include database routes
app.include_router(database_router)
)''',
    '''    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="scraper/static"), name="static")

# Include database routes
app.include_router(database_router)''')

# Write back
with open(web_api_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed syntax error in web_api.py")

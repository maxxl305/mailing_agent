#!/usr/bin/env python3
# start_tool.py - Ein-Klick-Start für das Company Research Tool

import subprocess
import sys
import os
import webbrowser
import time
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import reportlab
        import docx
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing FastAPI dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "fastapi>=0.104.1",
            "uvicorn[standard]>=0.24.0", 
            "websockets>=12.0",
            "python-multipart>=0.0.6",
            "reportlab>=4.0.7",
            "python-docx>=1.1.0",
            "python-dotenv>=1.0.0"
        ])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting Company Research Tool...")
    
    # Create necessary directories
    Path("exports").mkdir(exist_ok=True)
    
    try:
        # Import here to avoid import errors during dependency check
        import uvicorn
        from app import app
        
        print("💻 Server will be available at: http://localhost:8000")
        print("🔄 Opening browser in 3 seconds...")
        
        # Open browser after short delay
        def open_browser():
            time.sleep(3)
            webbrowser.open("http://localhost:8000")
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Start server
        uvicorn.run(app, host="127.0.0.1", port=8000, reload=False, log_level="info")
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

def main():
    """Main function"""
    print("🔍 COMPANY RESEARCH TOOL")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("src/agent").exists():
        print("❌ Error: Please run this script from the project root directory")
        print("   (where src/agent/ folder is located)")
        sys.exit(1)
    
    # Check .env file
    if not Path(".env").exists():
        print("⚠️  Warning: .env file not found")
        print("   Please create .env with your API keys:")
        print("   FIRECRAWL_API_KEY=your_key_here")
        print("   OPENAI_API_KEY=your_key_here")
        print("   TAVILY_API_KEY=your_key_here")
        
        create_env = input("\n❓ Continue anyway? (y/n): ").lower().strip()
        if create_env != 'y':
            print("👋 Setup cancelled.")
            sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("📦 Some dependencies are missing.")
        install = input("❓ Install them now? (y/n): ").lower().strip()
        
        if install == 'y':
            if not install_dependencies():
                print("❌ Failed to install dependencies. Please install manually:")
                print("   pip install -r requirements_fastapi.txt")
                sys.exit(1)
        else:
            print("👋 Installation cancelled.")
            sys.exit(1)
    
    # Start the server
    start_server()

if __name__ == "__main__":
    main()
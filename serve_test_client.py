#!/usr/bin/env python3
"""
Simple HTTP server to serve the web test client
"""
import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

def serve_test_client():
    """Serve the web test client on localhost."""
    
    # Check if the HTML file exists
    html_file = Path("web_test_client.html")
    if not html_file.exists():
        print("❌ web_test_client.html not found!")
        print("Please make sure the file exists in the current directory.")
        return
    
    # Set up the server
    PORT = 8080
    
    # Change to the directory containing the HTML file
    os.chdir(Path.cwd())
    
    # Create a custom handler to serve the HTML file
    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                self.path = '/web_test_client.html'
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
    
    try:
        with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
            print(f"🌐 Web Test Client Server")
            print("=" * 50)
            print(f"✅ Server started on http://localhost:{PORT}")
            print(f"📁 Serving: {html_file.absolute()}")
            print("\n🚀 Opening browser automatically...")
            print("   If browser doesn't open, go to: http://localhost:8080")
            print("\n📋 Instructions:")
            print("   1. Make sure your FastAPI server is running on http://localhost:8000")
            print("   2. Register a new user or login with existing credentials")
            print("   3. Create a project to get a project ID")
            print("   4. Start testing the chatbot endpoints!")
            print("\n⏹️  Press Ctrl+C to stop the server")
            print("=" * 50)
            
            # Open browser automatically
            webbrowser.open(f'http://localhost:{PORT}')
            
            # Start serving
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {PORT} is already in use!")
            print("   Please stop any other server using this port or change the port number.")
        else:
            print(f"❌ Server error: {e}")

if __name__ == "__main__":
    serve_test_client() 
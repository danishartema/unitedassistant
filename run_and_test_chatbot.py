#!/usr/bin/env python3
"""
Run and Test Chatbot Service
Starts the server and runs comprehensive tests
"""
import subprocess
import time
import requests
import json
import sys
import os
from pathlib import Path

class ChatbotRunner:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.server_process = None
        
    def check_dependencies(self):
        """Check if required files exist"""
        print("🔍 Checking dependencies...")
        
        required_files = [
            "main.py",
            "services/chatbot_service.py",
            "routers/assistant.py",
            "config.py",
            "database.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            print("❌ Missing required files:")
            for file in missing_files:
                print(f"   - {file}")
            return False
        
        print("✅ All required files found")
        return True
    
    def check_gpt_flow_directory(self):
        """Check if GPT FINAL FLOW directory exists"""
        print("🔍 Checking GPT FINAL FLOW directory...")
        
        gpt_flow_path = Path("GPT FINAL FLOW")
        if not gpt_flow_path.exists():
            print("❌ GPT FINAL FLOW directory not found")
            return False
        
        # Check for at least one module
        modules = list(gpt_flow_path.glob("*_*"))
        if not modules:
            print("❌ No modules found in GPT FINAL FLOW directory")
            return False
        
        print(f"✅ Found {len(modules)} modules in GPT FINAL FLOW")
        for module in modules[:3]:  # Show first 3
            print(f"   - {module.name}")
        
        return True
    
    def start_server(self):
        """Start the FastAPI server"""
        print("🚀 Starting FastAPI server...")
        
        try:
            # Start server in background
            self.server_process = subprocess.Popen(
                [sys.executable, "main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start
            print("⏳ Waiting for server to start...")
            time.sleep(5)
            
            # Check if server is running
            try:
                response = requests.get(f"{self.base_url}/health", timeout=10)
                if response.status_code == 200:
                    print("✅ Server is running successfully!")
                    return True
                else:
                    print(f"❌ Server responded with status: {response.status_code}")
                    return False
            except requests.exceptions.RequestException as e:
                print(f"❌ Server not responding: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False
    
    def test_basic_endpoints(self):
        """Test basic endpoints"""
        print("\n🧪 Testing Basic Endpoints")
        print("-" * 30)
        
        tests = [
            ("Health Check", "/health"),
            ("Root Endpoint", "/"),
            ("List Modes", "/api/v1/assistant/modes"),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, endpoint in tests:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                success = response.status_code == 200
                print(f"{'✅' if success else '❌'} {test_name}: {response.status_code}")
                
                if success:
                    passed += 1
                    if endpoint == "/api/v1/assistant/modes":
                        data = response.json()
                        modules = data.get('modules', [])
                        print(f"   Found {len(modules)} modules")
                else:
                    failed += 1
                    
            except Exception as e:
                print(f"❌ {test_name}: {e}")
                failed += 1
        
        return passed, failed
    
    def test_chatbot_functionality(self):
        """Test chatbot functionality"""
        print("\n🤖 Testing Chatbot Functionality")
        print("-" * 30)
        
        try:
            # Test getting modules
            response = requests.get(f"{self.base_url}/api/v1/assistant/modes", timeout=10)
            if response.status_code != 200:
                print(f"❌ Failed to get modules: {response.status_code}")
                return False
            
            data = response.json()
            modules = data.get('modules', [])
            
            if not modules:
                print("❌ No modules found")
                return False
            
            print(f"✅ Found {len(modules)} modules")
            
            # Test getting module info for first module
            first_module = modules[0]
            module_name = first_module.get('name', 'Unknown')
            print(f"✅ Testing module: {module_name}")
            
            # Test module info endpoint
            module_id = "1_The Offer Clarifier GPT"
            info_response = requests.get(
                f"{self.base_url}/api/v1/assistant/modules/{module_id}/info",
                timeout=10
            )
            
            if info_response.status_code == 200:
                info_data = info_response.json()
                question_count = info_data.get('question_count', 0)
                print(f"✅ Module info retrieved: {question_count} questions")
                return True
            else:
                print(f"❌ Failed to get module info: {info_response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing chatbot functionality: {e}")
            return False
    
    def stop_server(self):
        """Stop the server"""
        if self.server_process:
            print("🛑 Stopping server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=10)
                print("✅ Server stopped")
            except subprocess.TimeoutExpired:
                print("⚠️  Server didn't stop gracefully, forcing...")
                self.server_process.kill()
    
    def run_full_test(self):
        """Run the complete test suite"""
        print("🎯 Chatbot Service Full Test")
        print("=" * 50)
        
        # Check dependencies
        if not self.check_dependencies():
            print("❌ Dependency check failed. Cannot continue.")
            return False
        
        # Check GPT FLOW directory
        if not self.check_gpt_flow_directory():
            print("❌ GPT FLOW directory check failed. Cannot continue.")
            return False
        
        # Start server
        if not self.start_server():
            print("❌ Server start failed. Cannot continue.")
            return False
        
        try:
            # Test basic endpoints
            basic_passed, basic_failed = self.test_basic_endpoints()
            
            # Test chatbot functionality
            chatbot_success = self.test_chatbot_functionality()
            
            # Summary
            print("\n" + "=" * 50)
            print("📊 Test Results Summary")
            print("=" * 50)
            print(f"Basic Endpoints: {basic_passed} passed, {basic_failed} failed")
            print(f"Chatbot Functionality: {'✅ PASS' if chatbot_success else '❌ FAIL'}")
            
            total_passed = basic_passed + (1 if chatbot_success else 0)
            total_tests = basic_passed + basic_failed + 1
            
            print(f"\nOverall: {total_passed}/{total_tests} tests passed")
            
            if total_passed == total_tests:
                print("🎉 All tests passed! Chatbot service is working perfectly!")
                print("\n✨ What's Working:")
                print("   ✅ Server is running and healthy")
                print("   ✅ All basic endpoints are accessible")
                print("   ✅ Chatbot modules are loaded")
                print("   ✅ Module information is accessible")
                print("   ✅ Ready for interactive testing!")
                
                print("\n🚀 Next Steps:")
                print("   1. Run 'python chatbot_interactive_test.py' for interactive testing")
                print("   2. Run 'python test_chatbot_comprehensive.py' for full workflow testing")
                print("   3. Access the API docs at http://localhost:8000/docs")
                
                return True
            else:
                print(f"⚠️  {total_tests - total_passed} tests failed. Check the output above.")
                return False
                
        finally:
            # Always stop the server
            self.stop_server()

if __name__ == "__main__":
    runner = ChatbotRunner()
    success = runner.run_full_test()
    
    if success:
        print("\n🎉 Chatbot service test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Chatbot service test failed!")
        sys.exit(1) 
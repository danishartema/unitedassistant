#!/usr/bin/env python3
"""
Direct GPT Chat - Test GPT model directly without API
"""
import os
import sys
from openai import OpenAI
from typing import Optional

class DirectGPTChat:
    def __init__(self):
        # Get API key from environment
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            print("❌ OPENAI_API_KEY not found in environment variables")
            print("Please set your OpenAI API key:")
            print("   export OPENAI_API_KEY=sk-your-key-here")
            print("   or create a .env file with: OPENAI_API_KEY=sk-your-key-here")
            sys.exit(1)
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o"  # Using the same model as your chatbot
        
    def test_connection(self):
        """Test if we can connect to OpenAI"""
        try:
            print("🔗 Testing OpenAI connection...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello! Just testing the connection."}],
                max_tokens=50
            )
            print("✅ Successfully connected to OpenAI!")
            print(f"   Model: {self.model}")
            print(f"   Response: {response.choices[0].message.content}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to OpenAI: {e}")
            return False
    
    def chat(self):
        """Interactive chat with GPT"""
        print(f"\n🤖 Direct Chat with {self.model}")
        print("=" * 50)
        print("You can now chat directly with the GPT model!")
        print("Type 'quit' to exit")
        print("=" * 50)
        
        conversation_history = []
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                print("🤖 Thinking...")
                
                # Add user message to history
                conversation_history.append({"role": "user", "content": user_input})
                
                # Get response from GPT
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=conversation_history,
                    max_tokens=1000,
                    temperature=0.7
                )
                
                # Get the response
                assistant_response = response.choices[0].message.content
                
                # Add assistant response to history
                conversation_history.append({"role": "assistant", "content": assistant_response})
                
                # Print response
                print(f"\nGPT: {assistant_response}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                # Remove the last user message if there was an error
                if conversation_history:
                    conversation_history.pop()
    
    def test_chatbot_prompts(self):
        """Test with chatbot-style prompts"""
        print(f"\n🧪 Testing Chatbot-Style Prompts with {self.model}")
        print("=" * 50)
        
        test_prompts = [
            "What is your product, service, or offer called?",
            "Who is your ideal customer?",
            "What are the biggest frustrations your customers face?",
            "What transformation do your customers experience?",
            "What makes your offer different from others?"
        ]
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n📝 Test {i}: {prompt}")
            print("-" * 40)
            
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful business consultant asking clarifying questions to help users define their products and services."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=200,
                    temperature=0.7
                )
                
                print(f"GPT Response: {response.choices[0].message.content}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("\n✅ Chatbot prompt testing complete!")

def main():
    """Main function"""
    print("🚀 Direct GPT Chat Test")
    print("=" * 50)
    
    chat = DirectGPTChat()
    
    # Test connection first
    if not chat.test_connection():
        return
    
    print("\n" + "=" * 50)
    print("Choose your test:")
    print("1. Interactive chat")
    print("2. Test chatbot prompts")
    print("3. Both")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        chat.chat()
    elif choice == "2":
        chat.test_chatbot_prompts()
    elif choice == "3":
        chat.test_chatbot_prompts()
        print("\n" + "=" * 50)
        chat.chat()
    elif choice == "4":
        print("👋 Goodbye!")
    else:
        print("Invalid choice. Exiting.")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Check environment variables and help set up API keys
"""

import os
import sys

def check_environment():
    """Check environment variables"""
    print("=" * 60)
    print("ENVIRONMENT VARIABLE CHECK")
    print("=" * 60)
    
    # Check OpenAI API key
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        print(f"✓ OPENAI_API_KEY found: {openai_key[:10]}...")
    else:
        print("✗ OPENAI_API_KEY not found")
    
    # Check Google credentials
    google_creds = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if google_creds:
        print(f"✓ GOOGLE_APPLICATION_CREDENTIALS found: {google_creds}")
    else:
        print("✗ GOOGLE_APPLICATION_CREDENTIALS not found")
    
    # Check if default Google credentials file exists
    if os.path.exists('sampark-ai-bc13b9af3b55.json'):
        print("✓ Google credentials file found: sampark-ai-bc13b9af3b55.json")
    else:
        print("✗ Google credentials file not found: sampark-ai-bc13b9af3b55.json")
    
    print("\n" + "=" * 60)
    print("ALL ENVIRONMENT VARIABLES")
    print("=" * 60)
    
    # Show all environment variables
    for key, value in sorted(os.environ.items()):
        if 'OPENAI' in key.upper() or 'GOOGLE' in key.upper() or 'API' in key.upper():
            print(f"{key}: {value[:20]}..." if len(value) > 20 else f"{key}: {value}")
    
    print("\n" + "=" * 60)
    print("SETUP INSTRUCTIONS")
    print("=" * 60)
    
    if not openai_key:
        print("To set your OpenAI API key:")
        print("  PowerShell: $env:OPENAI_API_KEY='your-key-here'")
        print("  Command Prompt: set OPENAI_API_KEY=your-key-here")
        print("  Linux/Mac: export OPENAI_API_KEY='your-key-here'")
        print()
        print("Then run: python real_api_test.py")

if __name__ == "__main__":
    check_environment()

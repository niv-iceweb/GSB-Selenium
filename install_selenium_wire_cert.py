#!/usr/bin/env python3
"""
Install selenium-wire certificate to fix SSL warnings.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def install_certificate_macos(cert_path):
    """Install certificate on macOS."""
    try:
        # Add to system keychain
        cmd = [
            "sudo", "security", "add-trusted-cert", 
            "-d", "-r", "trustRoot",
            "-k", "/Library/Keychains/System.keychain",
            str(cert_path)
        ]
        
        print("Installing certificate to system keychain (requires sudo)...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Certificate installed successfully in system keychain")
        else:
            print(f"❌ Failed to install in system keychain: {result.stderr}")
            
        # Also add to user keychain as backup
        user_cmd = [
            "security", "add-trusted-cert",
            "-d", "-r", "trustRoot", 
            "-k", "~/Library/Keychains/login.keychain",
            str(cert_path)
        ]
        
        print("Installing certificate to user keychain...")
        user_result = subprocess.run(user_cmd, capture_output=True, text=True)
        
        if user_result.returncode == 0:
            print("✅ Certificate installed successfully in user keychain")
            return True
        else:
            print(f"⚠️ Failed to install in user keychain: {user_result.stderr}")
            return result.returncode == 0
            
    except Exception as e:
        print(f"❌ Error installing certificate: {e}")
        return False

def install_certificate_linux(cert_path):
    """Install certificate on Linux."""
    try:
        # Copy to system certificate directory
        cert_dir = Path("/usr/local/share/ca-certificates")
        if not cert_dir.exists():
            cert_dir = Path("/etc/ssl/certs")
            
        target_path = cert_dir / "selenium-wire.crt"
        
        cmd = ["sudo", "cp", str(cert_path), str(target_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Failed to copy certificate: {result.stderr}")
            return False
            
        # Update certificate store
        update_cmd = ["sudo", "update-ca-certificates"]
        update_result = subprocess.run(update_cmd, capture_output=True, text=True)
        
        if update_result.returncode == 0:
            print("✅ Certificate installed successfully on Linux")
            return True
        else:
            print(f"❌ Failed to update certificates: {update_result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error installing certificate: {e}")
        return False

def main():
    """Main installation function."""
    print("🔧 Installing selenium-wire certificate to fix SSL warnings...")
    
    # Check if certificate exists
    cert_path = Path("ca.crt")
    if not cert_path.exists():
        print("❌ Certificate file 'ca.crt' not found!")
        print("Run: poetry run python -m seleniumwire extractcert")
        sys.exit(1)
    
    print(f"📄 Found certificate: {cert_path.absolute()}")
    
    # Detect OS and install
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        print("🍎 Detected macOS")
        success = install_certificate_macos(cert_path)
    elif system == "linux":
        print("🐧 Detected Linux") 
        success = install_certificate_linux(cert_path)
    elif system == "windows":
        print("🪟 Detected Windows")
        print("For Windows, run: certutil -addstore -f \"Root\" ca.crt")
        print("Or manually import ca.crt into Chrome's certificate store")
        return
    else:
        print(f"❓ Unknown system: {system}")
        print("Please manually install ca.crt into your system's certificate store")
        return
    
    if success:
        print("\n✅ Certificate installation completed!")
        print("🔄 You may need to restart Chrome for changes to take effect")
        print("🧪 Test with: poetry run gsb run --searches 1")
    else:
        print("\n❌ Certificate installation failed!")
        print("You may need to manually install the certificate")

if __name__ == "__main__":
    main()
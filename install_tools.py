import os
import subprocess
import sys

def run_command(cmd, shell=False):
    print(f"Executing: {cmd}")
    try:
        subprocess.run(cmd, shell=shell, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def install_wsl_tools():
    print("\n--- Installing Tools in WSL (Ubuntu) ---")
    update_cmd = "wsl -u root apt update"
    run_command(update_cmd)
    
    tools = [
        "nmap",
        "sqlmap",
        "hydra",
        "nikto",
        "gobuster",
        "metasploit-framework",
        "john"
    ]
    
    install_cmd = f"wsl -u root apt install -y {' '.join(tools)}"
    run_command(install_cmd)

def install_windows_tools():
    print("\n--- Installing Tools in Windows ---")
    # Using winget for common tools
    tools = [
        "Insecure.Nmap",
        "WiresharkFoundation.Wireshark"
    ]
    
    for tool in tools:
        cmd = f"winget install --id {tool} --silent --accept-package-agreements --accept-source-agreements"
        run_command(cmd)

if __name__ == "__main__":
    print("E.D.I.T.H - Cybersecurity Tool Installer")
    
    # Create tools directory if not exists
    if not os.path.exists("tools"):
        os.makedirs("tools")
        
    try:
        install_wsl_tools()
    except Exception as e:
        print(f"WSL Installation failed: {e}")
        
    try:
        install_windows_tools()
    except Exception as e:
        print(f"Windows Installation failed: {e}")
        
    print("\nInstallation complete! You can now use these tools in your E.D.I.T.H terminal.")

import subprocess
import shutil
import time
import re

# Global process reference
cloudflared_process = None

def setup_cloudflared(port):
    """Set up a Cloudflare Tunnel for the specified port."""
    global cloudflared_process
    
    # Check if cloudflared is installed
    if not shutil.which("cloudflared"):
        print("\n--------------------------------------------------------")
        print("Error: cloudflared is not installed")
        print("Please install it with:")
        print("macOS: brew install cloudflared")
        print("Linux: Follow the instructions at Cloudflare's website")
        print("--------------------------------------------------------\n")
        raise Exception("cloudflared not installed")
    
    # Start cloudflared tunnel
    print("Setting up Cloudflare Tunnel...")
    
    process = subprocess.Popen(
        ["cloudflared", "tunnel", "--no-autoupdate", "--url", f"http://localhost:{port}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    cloudflared_process = process
    
    # Wait for tunnel to establish and find URL
    print("Waiting for tunnel to establish...")
    
    public_url = None
    output_buffer = []
    
    # Try for 20 seconds to find the URL
    for _ in range(20):
        # Check if process has exited
        if process.poll() is not None:
            error_output = "\n".join(output_buffer[-10:])
            
            # Check for common connection issues
            if "context deadline exceeded" in error_output or "Client.Timeout exceeded" in error_output:
                print("\n--------------------------------------------------------")
                print("ERROR: Cannot connect to Cloudflare API")
                print("This could be due to:")
                print("1. VPN blocking Cloudflare connections (most common cause)")
                print("   - Please disable your VPN and try again")
                print("2. Network connectivity issues")
                print("3. Temporary Cloudflare service disruption")
                print("--------------------------------------------------------\n")
            
            raise Exception(f"Cloudflared exited with error code {process.returncode}. Output: {error_output}")
            
        # Check stdout
        while True:
            line = process.stdout.readline().strip()
            if not line:
                break
            
            output_buffer.append(line)
            # Look for URLs but exclude the generic API URL
            if "trycloudflare.com" in line and "api.trycloudflare.com" not in line:
                url_match = re.search(r'https://[-a-zA-Z0-9.]+\.trycloudflare\.com', line)
                if url_match and "api.trycloudflare.com" not in url_match.group(0):
                    public_url = url_match.group(0)
                    break
        
        # Found URL? Done!
        if public_url:
            break
            
        # Check stderr
        while True:
            line = process.stderr.readline().strip()
            if not line:
                break
            
            output_buffer.append(line)
            # Look for URLs but exclude the generic API URL
            if "trycloudflare.com" in line and "api.trycloudflare.com" not in line:
                url_match = re.search(r'https://[-a-zA-Z0-9.]+\.trycloudflare\.com', line)
                if url_match and "api.trycloudflare.com" not in url_match.group(0):
                    public_url = url_match.group(0)
                    break
        
        # Found URL? Done!
        if public_url:
            break
            
        # Wait before checking again
        time.sleep(1)
    
    # If we still don't have a URL, scan the whole buffer
    if public_url is None:
        for line in output_buffer:
            # Skip lines with the API URL
            if "api.trycloudflare.com" in line:
                continue
                
            url_match = re.search(r'https://[-a-zA-Z0-9.]+\.trycloudflare\.com', line)
            if url_match and "api.trycloudflare.com" not in url_match.group(0):
                public_url = url_match.group(0)
                break
    
    # If we still don't have a URL or got the generic API URL, warn but continue
    if public_url is None or public_url == "https://api.trycloudflare.com":
        if public_url == "https://api.trycloudflare.com":
            print("WARNING: Received generic API URL instead of a unique tunnel URL.")
            print("This typically happens when using a VPN that blocks Cloudflare connections.")
            print("Try disabling your VPN to get a proper tunnel URL.")
            
            # Debug: Let's try to find the actual URL in the output
            print("\nSearching for actual tunnel URL in output...")
            for line in output_buffer:
                if "trycloudflare.com" in line and "api.trycloudflare.com" not in line:
                    print(f"Potential URL line: {line}")
        else:
            print("WARNING: Couldn't determine the tunnel URL.")
            print("Check the console output for a URL like https://something.trycloudflare.com")
        
        # Use a placeholder URL
        public_url = "https://unknown.trycloudflare.com"
    
    print("\n--------------------------------------------------------")
    print(f"Cloudflare Tunnel URL: {public_url}")
    print("Share this URL to connect to your chat!")
    print("This tunnel will remain active until you press Ctrl+C")
    print("--------------------------------------------------------\n")
    
    return public_url

def cleanup_tunnel():
    """Terminate the Cloudflare Tunnel process if it's running."""
    global cloudflared_process
    
    if cloudflared_process is not None:
        print("Terminating Cloudflare Tunnel...")
        try:
            cloudflared_process.terminate()
            cloudflared_process.wait(timeout=5)
            print("Cloudflare Tunnel terminated successfully")
        except Exception as e:
            print(f"Error terminating Cloudflare Tunnel: {e}")
            try:
                cloudflared_process.kill()
            except:
                pass
        cloudflared_process = None

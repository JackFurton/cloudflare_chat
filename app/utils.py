import subprocess
import shutil
import time
import re
import logging
import signal
from typing import Optional, Tuple

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('chat_app')

# Global process reference
cloudflared_process: Optional[subprocess.Popen] = None

def setup_cloudflared(port: int) -> str:
    """
    Set up a Cloudflare Tunnel for the specified port.
    
    Args:
        port: The local port to expose via the tunnel
        
    Returns:
        str: The public URL for the tunnel
        
    Raises:
        Exception: If cloudflared is not installed or the tunnel cannot be established
    """
    global cloudflared_process
    
    # Check if cloudflared is installed
    if not shutil.which("cloudflared"):
        error_msg = (
            "\n--------------------------------------------------------\n"
            "Error: cloudflared is not installed\n"
            "Please install it with:\n"
            "macOS: brew install cloudflared\n"
            "Linux: Follow the instructions at Cloudflare's website\n"
            "--------------------------------------------------------"
        )
        logger.error(error_msg)
        raise Exception("cloudflared not installed")
    
    # Start cloudflared tunnel
    logger.info("Setting up Cloudflare Tunnel...")
    
    process = subprocess.Popen(
        ["cloudflared", "tunnel", "--no-autoupdate", "--url", f"http://localhost:{port}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    cloudflared_process = process
    
    # Wait for tunnel to establish and find URL
    logger.info("Waiting for tunnel to establish...")
    
    public_url, error = _extract_tunnel_url(process, timeout_seconds=20)
    
    if error:
        vpn_msg = (
            "\n--------------------------------------------------------\n"
            "ERROR: Cannot connect to Cloudflare API\n"
            "This could be due to:\n"
            "1. VPN blocking Cloudflare connections (most common cause)\n"
            "   - Please disable your VPN and try again\n"
            "2. Network connectivity issues\n"
            "3. Temporary Cloudflare service disruption\n"
            "--------------------------------------------------------"
        )
        logger.error(vpn_msg)
        raise Exception(f"Cloudflared error: {error}")
            
    # If we still don't have a URL or got the generic API URL, warn but continue
    if public_url is None or public_url == "https://api.trycloudflare.com":
        if public_url == "https://api.trycloudflare.com":
            logger.warning(
                "Received generic API URL instead of a unique tunnel URL. "
                "This typically happens when using a VPN that blocks Cloudflare connections. "
                "Try disabling your VPN to get a proper tunnel URL."
            )
        else:
            logger.warning(
                "Couldn't determine the tunnel URL. "
                "Check the console output for a URL like https://something.trycloudflare.com"
            )
        
        # Use a placeholder URL
        public_url = "https://unknown.trycloudflare.com"
    
    success_msg = (
        "\n--------------------------------------------------------\n"
        f"Cloudflare Tunnel URL: {public_url}\n"
        "Share this URL to connect to your chat!\n"
        "This tunnel will remain active until you press Ctrl+C\n"
        "--------------------------------------------------------"
    )
    logger.info(success_msg)
    
    return public_url

def _extract_tunnel_url(process: subprocess.Popen, timeout_seconds: int = 20) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract the tunnel URL from the cloudflared process output.
    
    Args:
        process: The cloudflared process
        timeout_seconds: Maximum time to wait for the URL
        
    Returns:
        Tuple containing:
            - The tunnel URL (or None if not found)
            - Error message (or None if no error)
    """
    output_buffer = []
    public_url = None
    
    # Try for the specified timeout to find the URL
    for _ in range(timeout_seconds):
        # Check if process has exited
        if process.poll() is not None:
            error_output = "\n".join(output_buffer[-10:])
            
            # Check for common connection issues
            if "context deadline exceeded" in error_output or "Client.Timeout exceeded" in error_output:
                return None, "Connection timeout"
            
            return None, f"Cloudflared exited with error code {process.returncode}. Output: {error_output}"
            
        # Check stdout
        url = _check_stream_for_url(process.stdout, output_buffer)
        if url:
            return url, None
            
        # Check stderr
        url = _check_stream_for_url(process.stderr, output_buffer)
        if url:
            return url, None
            
        # Wait before checking again
        time.sleep(1)
    
    # Timeout occurred - scan the whole buffer one more time
    for line in output_buffer:
        # Skip lines with the API URL
        if "api.trycloudflare.com" in line:
            continue
            
        url_match = re.search(r'https://[-a-zA-Z0-9.]+\.trycloudflare\.com', line)
        if url_match and "api.trycloudflare.com" not in url_match.group(0):
            return url_match.group(0), None
    
    return None, "Timed out waiting for tunnel URL"

def _check_stream_for_url(stream, output_buffer: list) -> Optional[str]:
    """
    Check a stream for a trycloudflare.com URL.
    
    Args:
        stream: The stdout or stderr stream to check
        output_buffer: Buffer to store output lines
        
    Returns:
        The URL if found, None otherwise
    """
    while True:
        line = stream.readline().strip()
        if not line:
            break
        
        output_buffer.append(line)
        # Look for URLs but exclude the generic API URL
        if "trycloudflare.com" in line and "api.trycloudflare.com" not in line:
            url_match = re.search(r'https://[-a-zA-Z0-9.]+\.trycloudflare\.com', line)
            if url_match and "api.trycloudflare.com" not in url_match.group(0):
                return url_match.group(0)
    
    return None

def cleanup_tunnel() -> None:
    """Terminate the Cloudflare Tunnel process if it's running."""
    global cloudflared_process
    
    if cloudflared_process is not None:
        logger.info("Terminating Cloudflare Tunnel...")
        try:
            # Send SIGTERM
            cloudflared_process.terminate()
            try:
                cloudflared_process.wait(timeout=5)
                logger.info("Cloudflare Tunnel terminated successfully")
            except subprocess.TimeoutExpired:
                # If SIGTERM doesn't work, use SIGKILL
                logger.warning("Tunnel didn't terminate gracefully, forcing kill")
                cloudflared_process.kill()
                cloudflared_process.wait(timeout=2)
                logger.info("Cloudflare Tunnel forcefully terminated")
        except Exception as e:
            logger.error(f"Error terminating Cloudflare Tunnel: {e}")
            try:
                # Final attempt with SIGKILL
                cloudflared_process.kill()
            except:
                pass
        cloudflared_process = None
from logger import logger
from config import LOG_FILE

class ContainmentManager:
    def __init__(self):
        self.isolated_devices = set()
        
    def isolate_device(self, ip_address):
        """Autonomously disconnects compromised devices via logical isolation"""
        if ip_address not in self.isolated_devices:
            self.isolated_devices.add(ip_address)
            # Log this directly to the file without printing to avoid duplication
            logger.warning(f"Device '{ip_address}' ISOLATED from network due to confirmed threat.")
            return True
        return False
        
    def log_file_ref(self):
        return LOG_FILE

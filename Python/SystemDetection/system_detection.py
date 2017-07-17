import sys
import platform


class SystemDetection(object):
    def __init__(self):
        self.system_info = {
            "Python Version": sys.version.split('\n'),
            "Dist": str(platform.dist()),
            "Linux Distro": SystemDetection.linux_distribution(),
            "Platform": platform.platform(),
            "System": platform.system(),
            "Machine": platform.machine(),
            "UName": platform.uname(),
            "Version": platform.version(),
            "Mac Version": platform.mac_ver()
        }

    @staticmethod
    def linux_distribution():
        try:
            return platform.linux_distribution()
        except:
            return "N/A"

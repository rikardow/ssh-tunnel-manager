import os

CONFIG_DIR = os.path.expanduser("~/.ssh-tunnel-manager")
CONF_FILE = os.path.join(CONFIG_DIR, "config.yml")
ICONS_DIR = os.path.join(CONFIG_DIR, "icons")

class LANG:
    TITLE = "SSH Tunnel Manager"
    START = "Start"
    STOP = "Stop"
    ADD = "Add"
    CLOSE = "Close"
    KILL_SSH = "Kill All SSH Processes"
    ALREADY_RUNNING = "SSH Tunnel Manager is already running"
    OOPS = "Oops!"
    CONF_NOT_FOUND = F"Config file not found. Creating default configuration in {CONFIG_DIR}"

class KEYS:
    REMOTE_ADDRESS = "remote_address"
    LOCAL_PORT = "local_port"
    PROXY_HOST = "proxy_host"
    BROWSER_OPEN = "browser_open"
    NAME = "name"
    ICON = "icon"

class ICONS:
    TUNNEL = ":icons/tunnel.png"
    START = ":icons/start.png"
    STOP = ":icons/stop.png"
    KILL_SSH = ":icons/kill.png"

class CMDS:    
    SSH = "ssh"
    SSH_KILL_NIX = "killall ssh"
    SSH_KILL_WIN = "taskkill /im ssh.exe /t /f"

# SSH Tunnel Manager

A cross-platform, PyQt GUI to manage SSH tunnels

![SSH Tunnel Manager](.screenshot.png)

## Installation (Standalone)

You can download the standalone executable from the [Release](https://github.com/mdminhazulhaque/ssh-tunnel-manager/releases) section.

## Installation (From Source)

* Install dependencies: `pip install -r requirements.txt`
* Run the app: `python3 app.py`
* The app will automatically create the configuration directory at `~/.ssh-tunnel-manager/`
* You can modify `sshtunnelmgr.desktop` and put in `~/.local/share/application` to create a app menu shortcut

## Configuration

The application stores configuration in `~/.ssh-tunnel-manager/config.yml`. On first run, it will be created automatically with a sample configuration.

A sample configuration file is also provided as `config.example.yml`. Here is one sample host entry:

```yaml
rabbitmq:
  browser_open: http://127.0.0.1
  local_port: 15672
  proxy_host: demo-bastion
  remote_address: 10.10.10.30:15672
```

This entry, when clicked `Start`, will run the following SSH command to establish the tunnel.

```
ssh -L 127.0.0.1:15672:10.10.10.30:15672 demo-bastion
```

The key `browser_open` is optional. If provided, it will open the provided URL in the system's default web browser. (The `local_port` will be appended to the URL automatically!)

The application saves the tunnel information into a `dict` and can `kill` it when the `Stop` button is clicked.

### Adding New Tunnels

You can add new tunnel configurations directly from the GUI using the "Add" button. This will open a dialog where you can enter:
- Tunnel name
- Remote address (e.g., localhost:3306)
- Local port
- Proxy host (e.g., user@server)
- Browser URL (optional)

## SSH bind on Privileged Ports

Binding on privileged ports will fail unless the user/program has administrative access.

For Linux/macOS, run the following command to allow SSH program to allow binding on privileged ports.

```bash
sudo setcap CAP_NET_BIND_SERVICE=+eip /usr/bin/ssh
```

## Icons

The application looks for custom icons in the following locations (in order):
1. `~/.ssh-tunnel-manager/icons/` (user directory)
2. `./icons/` (application directory)

If you put image files (png/jpg/bmp) with the same filename as the tunnel name, it will appear as icon for that specific entry.

For example, if the tunnel identifier is `kubernetes`, then `kubernetes.png` will be used as the icon.

You can also specify a custom icon in the configuration:
```yaml
my_tunnel:
  icon: custom_icon.png
  # ... other config
```

## Migration

If you are migrating from older versions of this tool, please change all `local_address` in your config to `local_port` and make it a number.

## TODO

* Gracefully close SSH session instead of `kill`
* Store the config in `QSettings` instead of local yml file

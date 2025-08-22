#!/usr/bin/python3

# -*- coding: utf-8 -*-

__author__ = "Md. Minhazul Haque"
__license__ = "GPLv3"

import glob
import os
import requests
import shutil
import sys
import time
import yaml
from PyQt5.QtCore import QProcess, Qt, QUrl, QSharedMemory
from PyQt5.QtGui import QIcon, QDesktopServices, QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QApplication, QGridLayout, QDialog, QMessageBox, QSpinBox, QVBoxLayout, QHBoxLayout
from deepdiff import DeepDiff
from urllib.parse import urlparse

from tunnel import Ui_Tunnel
from tunnelconfig import Ui_TunnelConfig
from vars import CONF_FILE, CONFIG_DIR, ICONS_DIR, LANG, KEYS, ICONS, CMDS
import icons


def initialize_config():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

    if not os.path.exists(ICONS_DIR):
        os.makedirs(ICONS_DIR)

    if not os.path.exists(CONF_FILE):
        current_config = os.path.join(os.path.dirname(__file__), "config.yml")
        if os.path.exists(current_config):
            shutil.copy2(current_config, CONF_FILE)
        else:
            default_config = {
                "example": {
                    "remote_address": "localhost:22",
                    "local_port": 2222,
                    "proxy_host": "user@server",
                    "browser_open": ""
                }
            }
            with open(CONF_FILE, "w") as fp:
                yaml.dump(default_config, fp)

    icons_source = os.path.join(os.path.dirname(__file__), "icons")
    if os.path.exists(icons_source):
        for icon_file in os.listdir(icons_source):
            if icon_file.endswith(('.png', '.jpg', '.jpeg', '.svg')):
                source_path = os.path.join(icons_source, icon_file)
                dest_path = os.path.join(ICONS_DIR, icon_file)
                if not os.path.exists(dest_path):
                    shutil.copy2(source_path, dest_path)

def get_icon_path(icon_name):
    if not icon_name:
        return ICONS.TUNNEL

    user_icon_path = os.path.join(ICONS_DIR, icon_name)
    if os.path.exists(user_icon_path):
        return user_icon_path

    user_icon_png = os.path.join(ICONS_DIR, f"{icon_name}.png")
    if os.path.exists(user_icon_png):
        return user_icon_png

    local_icon_path = os.path.join("./icons", icon_name)
    if os.path.exists(local_icon_path):
        return local_icon_path

    local_icon_png = os.path.join("./icons", f"{icon_name}.png")
    if os.path.exists(local_icon_png):
        return local_icon_png

    return ICONS.TUNNEL

class TunnelConfig(QDialog):
    def __init__(self, parent, data):
        super(TunnelConfig, self).__init__(parent)
        
        self.ui = Ui_TunnelConfig()
        self.ui.setupUi(self)
        
        self.original_data = data

        self.ui.remote_address.setText(data.get(KEYS.REMOTE_ADDRESS))
        self.ui.proxy_host.setText(data.get(KEYS.PROXY_HOST))
        self.ui.browser_open.setText(data.get(KEYS.BROWSER_OPEN))
        self.ui.local_port.setValue(data.get(KEYS.LOCAL_PORT))
        
        self.ui.remote_address.textChanged.connect(self.render_ssh_command)
        self.ui.proxy_host.textChanged.connect(self.render_ssh_command)
        self.ui.local_port.valueChanged.connect(self.render_ssh_command)
        self.ui.copy.clicked.connect(self.do_copy_ssh_command)
        
        self.render_ssh_command()
    
    def render_ssh_command(self):
        ssh_command = F"ssh -L 127.0.0.1:{self.ui.local_port.value()}:{self.ui.remote_address.text()} {self.ui.proxy_host.text()}"
        self.ui.ssh_command.setText(ssh_command)
        
    def do_copy_ssh_command(self):
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(self.ui.ssh_command.text(), mode=cb.Clipboard)
        
    def as_dict(self):
        result = {
            KEYS.REMOTE_ADDRESS: self.ui.remote_address.text(),
            KEYS.PROXY_HOST: self.ui.proxy_host.text(),
            KEYS.BROWSER_OPEN: self.ui.browser_open.text(),
            KEYS.LOCAL_PORT: self.ui.local_port.value(),
        }

        if KEYS.NAME in self.original_data:
            result[KEYS.NAME] = self.original_data[KEYS.NAME]
        if KEYS.ICON in self.original_data:
            result[KEYS.ICON] = self.original_data[KEYS.ICON]

        return result

class Tunnel(QWidget):
    def __init__(self, name, data):
        super(Tunnel, self).__init__()
        
        self.ui = Ui_Tunnel()
        self.ui.setupUi(self)
        
        self.tunnelconfig = TunnelConfig(self, data)
        self.tunnelconfig.setWindowTitle(name)
        self.tunnelconfig.setModal(True)

        display_name = data.get(KEYS.NAME, name)
        self.ui.name.setText(display_name)

        custom_icon = data.get(KEYS.ICON)
        if custom_icon:
            icon_path = get_icon_path(custom_icon)
        else:
            icon_path = get_icon_path(name)

        self.ui.icon.setPixmap(QPixmap(icon_path))
        self.ui.action_tunnel.clicked.connect(self.do_tunnel)
        self.ui.action_settings.clicked.connect(self.tunnelconfig.show)
        self.ui.action_open.clicked.connect(self.do_open_browser)
        
        self.process = None
        
    def do_open_browser(self):
        browser_open = self.tunnelconfig.ui.browser_open.text()
        if browser_open:
            urlobj = urlparse(browser_open)
            local_port = self.tunnelconfig.ui.local_port.value()
            new_url = urlobj._replace(netloc=F"{urlobj.hostname}:{local_port}").geturl()
            QDesktopServices.openUrl(QUrl(new_url))
        
    def do_tunnel(self):
        if self.process:
            self.stop_tunnel()
        else:
            self.start_tunnel()
    
    def start_tunnel(self):
        params = self.tunnelconfig.ui.ssh_command.text().split(" ")
        
        self.process = QProcess()
        self.process.start(params[0], params[1:])
                    
        self.ui.action_tunnel.setIcon(QIcon(ICONS.STOP))
        
        self.do_open_browser()
    
    def stop_tunnel(self):
        try:
            self.process.kill()
            self.process = None
        except:
            pass
        
        self.ui.action_tunnel.setIcon(QIcon(ICONS.START))
        
class TunnelManager(QWidget):
    def __init__(self):
        super().__init__()
        
        with open(CONF_FILE, "r") as fp:
            self.data = yaml.load(fp, Loader=yaml.FullLoader)

        self.grid = QGridLayout(self)
        self.tunnels = []
        
        i = 0  # Inicializar i antes del bucle
        for i, name in enumerate(sorted(self.data.keys())):
            tunnel = Tunnel(name, self.data[name])
            tunnel.original_key = name  # Store original key for saving
            self.tunnels.append(tunnel)
            self.grid.addWidget(tunnel, i, 0)
        
        button_layout = QHBoxLayout()

        self.add_button = QPushButton(LANG.ADD)
        self.add_button.setIcon(QIcon(ICONS.ADD))
        self.add_button.setFocusPolicy(Qt.NoFocus)
        self.add_button.clicked.connect(self.do_add_tunnel)
        button_layout.addWidget(self.add_button)

        self.kill_button = QPushButton(LANG.KILL_SSH)
        self.kill_button.setIcon(QIcon(ICONS.KILL_SSH))
        self.kill_button.setFocusPolicy(Qt.NoFocus)
        self.kill_button.clicked.connect(self.do_killall_ssh)
        button_layout.addWidget(self.kill_button)

        button_widget = QWidget()
        button_widget.setLayout(button_layout)
        self.grid.addWidget(button_widget, i+1, 0)

        self.setLayout(self.grid)
        self.resize(10, 10)
        self.setWindowTitle(LANG.TITLE)
        self.setWindowIcon(QIcon(ICONS.TUNNEL))
        self.show()
    
    def do_killall_ssh(self):
        for tunnel in self.tunnels:
            tunnel.stop_tunnel()
        if os.name == 'nt':
            os.system(CMDS.SSH_KILL_WIN)
        else:
            os.system(CMDS.SSH_KILL_NIX)

    def do_add_tunnel(self):
        dialog = AddTunnelDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            tunnel_name = dialog.get_tunnel_name()
            if not tunnel_name:
                QMessageBox.warning(self, LANG.OOPS, "Tunnel name cannot be empty!")
                return

            if tunnel_name in self.data:
                QMessageBox.warning(self, LANG.OOPS, "Tunnel name already exists!")
                return

            tunnel_data = dialog.get_tunnel_data()
            self.data[tunnel_name] = tunnel_data

            tunnel = Tunnel(tunnel_name, tunnel_data)
            tunnel.original_key = tunnel_name
            self.tunnels.append(tunnel)

            row = len(self.tunnels) - 1
            self.grid.addWidget(tunnel, row, 0)

            button_widget = self.grid.itemAtPosition(row + 1, 0).widget()
            self.grid.removeWidget(button_widget)
            self.grid.addWidget(button_widget, row + 1, 0)

            self.resize(10, 10)

            with open(CONF_FILE, "w") as fp:
                yaml.dump(self.data, fp)

    def closeEvent(self, event):
        data = {}
        for tunnel in self.tunnels:
            original_key = getattr(tunnel, 'original_key', tunnel.ui.name.text())
            data[original_key] = tunnel.tunnelconfig.as_dict()

        changed = DeepDiff(self.data, data, ignore_order=True)
        
        if changed:
            timestamp = int(time.time())
            shutil.copy(CONF_FILE, F"{CONF_FILE}-{timestamp}")
            with open(CONF_FILE, "w") as fp:
                yaml.dump(data, fp)
            backup_configs = glob.glob(F"{CONF_FILE}-*")
            if len(backup_configs) > 10:
                for config in sorted(backup_configs, reverse=True)[10:]:
                    os.remove(config)
        event.accept()

class AddTunnelDialog(QDialog):
    def __init__(self, parent):
        super(AddTunnelDialog, self).__init__(parent)

        self.setWindowTitle(LANG.ADD_NEW_TUNNEL)
        self.setModal(True)
        self.resize(400, 250)

        layout = QVBoxLayout(self)

        form_layout = QGridLayout()

        form_layout.addWidget(QLabel("Tunnel Name:"), 0, 0)
        self.name_edit = QLineEdit()
        form_layout.addWidget(self.name_edit, 0, 1)

        form_layout.addWidget(QLabel("Remote Address:"), 1, 0)
        self.remote_address_edit = QLineEdit()
        self.remote_address_edit.setPlaceholderText("localhost:3306")
        form_layout.addWidget(self.remote_address_edit, 1, 1)

        form_layout.addWidget(QLabel("Local Port:"), 2, 0)
        self.local_port_spin = QSpinBox()
        self.local_port_spin.setRange(1, 65535)
        self.local_port_spin.setValue(8080)
        form_layout.addWidget(self.local_port_spin, 2, 1)

        form_layout.addWidget(QLabel("Proxy Host:"), 3, 0)
        self.proxy_host_edit = QLineEdit()
        self.proxy_host_edit.setPlaceholderText("user@server")
        form_layout.addWidget(self.proxy_host_edit, 3, 1)

        form_layout.addWidget(QLabel("Browser Open:"), 4, 0)
        self.browser_open_edit = QLineEdit()
        self.browser_open_edit.setPlaceholderText("http://localhost:8080")
        form_layout.addWidget(self.browser_open_edit, 4, 1)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

    def get_tunnel_data(self):
        return {
            KEYS.REMOTE_ADDRESS: self.remote_address_edit.text(),
            KEYS.LOCAL_PORT: self.local_port_spin.value(),
            KEYS.PROXY_HOST: self.proxy_host_edit.text(),
            KEYS.BROWSER_OPEN: self.browser_open_edit.text()
        }

    def get_tunnel_name(self):
        return self.name_edit.text().strip()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    sm = QSharedMemory("3866273d-f4d5-4bf3-b27b-772ca7915a61")
    
    if not sm.create(1):
        mb = QMessageBox()
        mb.setIcon(QMessageBox.Information)
        mb.setText(LANG.ALREADY_RUNNING)
        mb.setWindowTitle(LANG.OOPS)
        mb.setStandardButtons(QMessageBox.Close)
        mb.show()
    else:
        initialize_config()

        if not os.path.exists(CONF_FILE):
            mb = QMessageBox()
            mb.setIcon(QMessageBox.Information)
            mb.setText(LANG.CONF_NOT_FOUND)
            mb.setWindowTitle(LANG.OOPS)
            mb.setStandardButtons(QMessageBox.Close)
            mb.show()
        else:
            tm = TunnelManager()

    sys.exit(app.exec_())

from mitmproxy import ctx, http
from config import Config
from datetime import datetime, timedelta
from plugins import Websites, UrlFilters, Programs
from threading import Thread
from time import sleep
import psutil
import os
import logging

HTML_MESSAGE = "<h1>Website blocked by Zen! <i>{}<i></h1><p>Block in duration until <b>{}</b></p>"

class Zen:

    def __init__(self, plugins):
        self.config = Config(plugins)
        self.plugins = plugins
        self.start_time = datetime.now()

    def _check_interception(self, flow):
        for plugin in self.plugins:
            check, content = plugin._check_interception(flow)
            if check == True:
                return True, content, ', '.join([f'plugin name: {plugin.name}', f'block_type: {plugin.block_m[plugin.block_type]}'])
        return False, flow, ''

    def kill_process_by_path(target_path):
        """Kill a process if its executable path matches the target path."""
        for process in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                process_path = process.info['exe']
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Handle exceptions that may occur when accessing process information
                continue

            if process_path and target_path in process_path:
                print(f"Killing process {process.info['name']} (PID {process.info['pid']})")
                try:
                    os.kill(process.info['pid'], 9)  # Send SIGKILL signal
                except OSError as e:
                    print(f"Error killing process: {e}")

    def load(self, loader):
        loader.add_option(
            name="args", typespec=str, default="", help="arguments"
        )

    def configure(self, updates):
        self.config.args = ctx.options.args
        for plugin, config in zip(self.plugins, list(self.config.run().values())):
            plugin.load_config(config)
        self.time = self.config.time
        self.end_time = (self.start_time + timedelta(minutes=self.config.time)).strftime('%I:%M %p')
        [plugin.pre_block() for plugin in self.plugins]
        Thread(target=self.is_running).start()

    def is_running(self):
        while True:
            if self.start_time + timedelta(minutes=self.time) < datetime.now():
                ctx.master.shutdown()
            sleep(1)

    def request(self, flow):
        check, content, cause = self._check_interception(flow)
        if check == True:
            flow.response = http.Response.make(
                200,
                HTML_MESSAGE.format(cause, self.end_time).encode(),
                {"Content-Type": "text/html"}
            )
        else:
            flow = content
            
plugins = [f(idx+1) for idx,f in enumerate([Websites, UrlFilters, Programs])]
addons = [Zen(plugins)]

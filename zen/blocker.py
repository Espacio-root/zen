from mitmproxy import ctx, http
from config import Config
from argparse import ArgumentParser
from datetime import datetime, timedelta
from plugins import Websites, UrlFilters, Programs
import logging

HTML_MESSAGE = "<h1>Website blocked by Zen!</h1><p>Block in duration until {}</p>"
""" logging.basicConfig(filename='/home/espacio/projects/zen/zen/debug.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s') """
""" logging.debug('Initiating script') """

class Zen:

    def __init__(self, plugins):
        self.config = Config(plugins)
        self.plugins = [plugin(idx+1) for idx, plugin in enumerate(plugins)]
        self.start_time = datetime.now()

    @staticmethod
    def _parse_time(time):
        return datetime.now() + timedelta(minutes=time)

    def _check_interception(self, flow):
        for plugin in self.plugins:
            if plugin.field_type == 'bool':
                if plugin._check_interception(flow) == True:
                    return True, flow
        return False, flow

    def load(self, loader):
        loader.add_option(
            name="args", typespec=str, default="", help="arguments"
        )

    def configure(self, updates):
        self.config.args = ctx.options.args
        for plugin, config in zip(self.plugins, list(self.config.run().values())):
            plugin.load_config(config)
        self.time = self.config.time

    def running(self):
        if self.start_time + timedelta(minutes=self.time) < datetime.now():
            ctx.master.shutdown()

    def request(self, flow):
        check, content = self._check_interception(flow)
        logging.info("It's working!")
        if check == True:
            flow.response = http.Response.make(
                200,
                HTML_MESSAGE.format(self._parse_time(self.time)).encode(),
                {"Content-Type": "text/html"}
            )
        else:
            flow = content
            
addons = [Zen([Websites, UrlFilters, Programs])]
""" Zen([Websites, UrlFilters, Programs]) """

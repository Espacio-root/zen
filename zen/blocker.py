from mitmproxy import ctx, http
from config import Config
from datetime import datetime, timedelta
from plugins import Websites, UrlFilters, Programs
import logging

HTML_MESSAGE = "<h1>Website blocked by Zen!</h1><p>Block in duration until {}</p>"

class Zen:

    def __init__(self, plugins):
        self.config = Config(plugins)
        self.plugins = plugins
        self.start_time = datetime.now()

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
        self.end_time = (self.start_time + timedelta(minutes=self.config.time)).strftime('%I:%M %p')

    def running(self):
        if self.start_time + timedelta(minutes=self.time) < datetime.now():
            ctx.master.shutdown()

    def request(self, flow):
        check, content = self._check_interception(flow)
        if check == True:
            flow.response = http.Response.make(
                200,
                HTML_MESSAGE.format(self.end_time).encode(),
                {"Content-Type": "text/html"}
            )
        else:
            logging.info("not blocking")
            flow = content
            
plugins = [f(idx+1) for idx,f in enumerate([Websites, UrlFilters, Programs])]
addons = [Zen(plugins)]

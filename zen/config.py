from argparse import ArgumentParser
from plugins.core import Websites, UrlFilters, Programs
from plugins.youtube import YoutubeChannel
import json
import os
import shlex
import logging

dir_name = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_CONFIG_PATH = f"{dir_name}/configs/base_config.json"


class Config:
    def __init__(self, plugins: list):
        self.base_path = BASE_CONFIG_PATH
        self.plugins = plugins
        self.args = None
        if not os.path.exists(BASE_CONFIG_PATH):
            self._write_config({})

    def _read_config(self) -> dict:
        with open(self.base_path, "r") as fp:
            return json.load(fp)

    def _write_config(self, content) -> None:
        with open(self.base_path, "w") as fp:
            json.dump(content, fp)

    def create_config(self, name: str, plugins: list) -> dict:
        plugins = [
            plugin.process_plugin(values) for plugin, values in zip(self.plugins, plugins)
        ]
        return {
            name[0]: {
                plugin.name.lower(): values for plugin, values in zip(self.plugins, plugins)
            }
        }

    def remove_config(self, name):
        config = self._read_config()
        if name in config.keys():
            self._write_config({k: v for k, v in config.items() if k != name})
        else:
            raise Exception(f"Config with name {name} does not exist")

    def get_config(self, name):
        config = self._read_config()
        if name in config.keys():
            return config[name]
        else:
            raise Exception(f"Config with name {name} does not exist")

    def get_configs(self, names):
        configs = [self.get_config(name) for name in names]
        c_conf = configs[0]
        for config in configs[1:]:
            for k, v in config.items():
                f = [plugin for plugin in self.plugins if plugin.name.lower() == k][0]
                try:
                    c_conf[k] = f.post_update(
                        f.update_add(f.pre_update(c_conf[k]), f.pre_update(v))
                    )
                except KeyError:
                    c_conf[k] = v
        return c_conf

    def update_config(self, name: list, plugins: list, method: str):
        config = self.get_configs(name)
        plugins = [
            plugin.process_plugin(values) for plugin, values in zip(self.plugins, plugins)
        ]
        for plugin, values in zip(self.plugins, plugins):
            fn = getattr(plugin, f"update_{method}")
            config[plugin.name.lower()] = plugin.post_update(
                fn(
                    plugin.pre_update(config[plugin.name.lower()]),
                    plugin.pre_update(values),
                )
            )
        return {name[0]: config}

    def parse_args(self):
        parser = ArgumentParser()
        parser.add_argument(
            "-c",
            "--config",
            dest="name",
            help="Name of config to use",
            required=True,
            nargs="+",
        )
        parser.add_argument(
            "-n", "--new", dest="create", action="store_true", help="Create new config"
        )
        parser.add_argument(
            "-r", "--remove", dest="remove", action="store_true", help="Remove config"
        )
        parser.add_argument(
            "-u",
            "--update",
            dest="update",
            action="store_true",
            help="Update existing config",
        )
        parser.add_argument(
            "-b",
            "--blocktype",
            dest="block_type",
            help="Type of block: whitelist(w) or blacklist(b). Represent different setting for different plugin by concatenating the block_type. Example: wbb",
            default="wbbw",
        )
        parser.add_argument(
            "-t",
            "--time",
            dest="time",
            help="Time for which to maintain block in minutes. Example: 30 45 180",
            default=2,
        )
        for plugin in self.plugins:
            parser.add_argument(
                f"-f{plugin.idx}",
                f"--{plugin.name.lower()}",
                dest=plugin.name.lower(),
                nargs="+",
                help=plugin.help,
                default=plugin.default,
            )
        args = (
            parser.parse_args()
            if not self.args
            else parser.parse_args(shlex.split(self.args))
        )
        return args

    def _add_subconfig(self, config):
        base_config = self._read_config()
        base_config.update(config)
        self._write_config(base_config)

    def _set_args(self, args):
        block_type = args.block_type
        if len(block_type) == 1:
            block_type *= len(self.plugins)
        elif len(block_type) < len(self.plugins):
            block_type += block_type[-1] * len(self.plugins) - len(block_type)
        for plugin, b_type in zip(self.plugins, block_type):
            plugin.block_type = b_type
        self.time = args.time

    def run(self):
        args = self.parse_args()
        self._set_args(args)
        if args.update:
            method = "subtract" if args.remove else "add"
            config = self.update_config(
                args.name,
                [getattr(args, plugin.name.lower()) for plugin in self.plugins],
                method,
            )
            self._add_subconfig(config)
        elif args.create:
            config = self.create_config(
                args.name, [getattr(args, plugin.name.lower()) for plugin in self.plugins]
            )
            self._add_subconfig(config)
        elif args.remove:
            self.remove_config(args.name)
        config = self.get_configs(args.name)

        return config


plugins = [
    plugin(idx + 1)
    for idx, plugin in enumerate([YoutubeChannel, Websites, UrlFilters, Programs])
]
if __name__ == "__main__":
    config = Config(plugins)
    print(config.run())

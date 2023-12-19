""" from configparser import ConfigParser """
from argparse import ArgumentParser
import json
import os
import re

dir_name = os.path.dirname(os.path.dirname(os.path.abspath("__file__")))
BASE_CONFIG_PATH = f"{dir_name}/configs/base_config.json"


class Config:
    def __init__(self):
        self.base_path = BASE_CONFIG_PATH
        if not os.path.exists(BASE_CONFIG_PATH):
            self._write_config({})

    def _read_config(self) -> dict:
        with open(self.base_path, "r") as fp:
            return json.load(fp)

    def _write_config(self, content) -> None:
        with open(self.base_path, "w") as fp:
            json.dump(content, fp)

    @staticmethod
    def _handle_websites(websites: list):
        return [
            website.strip() for website in websites if re.match(r"^https?://", website)
        ]

    @staticmethod
    def _handle_filters(filters: list):
        d_filters = {}
        filters = list(map(lambda x: [x.split(",")[0], x.split(",")[1:]], filters))
        for url, filter in filters:
            if url in d_filters:
                d_filters[url].extend(filter)
            else:
                d_filters[url] = filter
        return d_filters

    @staticmethod
    def _handle_apps(apps: list):
        return [app.strip() for app in apps if os.path.exists(app.strip())]

    def create_config(self, name: str, websites: list, filters: list, apps: list):
        websites = self._handle_websites(websites)
        filters = self._handle_filters(filters)
        apps = self._handle_apps(apps)

        n_config = {
            "name": name,
            "websites": websites,
            "filters": filters,
            "apps": apps,
        }
        return n_config

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

    @staticmethod
    def add(l1: list, l2: list) -> list:
        return list(set(l1 + l2))

    @staticmethod
    def subtract(l1: list, l2: list) -> list:
        return list(set([e for e in l1 if e not in l2]))

    @staticmethod
    def reverse_filters_op(filters: dict) -> str:
        res = []
        for w, fs in filters.items():
            for f in fs:
                res.append(f"{w},{f}")
        return res

    def update_config(
        self, name: str, websites: list, filters: list, apps: list, method: str
    ):
        if method == "add":
            fn = self.add
        elif method == "subtract":
            fn = self.subtract
        else:
            raise Exception(f"Method can only be add or subtract. {method} was passed.")

        p_config = self.get_config(name)
        n_config = self.create_config(name, websites, filters, apps)
        websites = fn(p_config["websites"], n_config["websites"])
        filters = fn(
            self.reverse_filters_op(p_config["filters"]),
            self.reverse_filters_op(n_config["filters"]),
        )
        filters = self._handle_filters(filters)
        apps = fn(p_config["apps"], n_config["apps"])
        return {"name": name, "websites": websites, "filters": filters, "apps": apps}

    def parse_args(self):
        parser = ArgumentParser()
        parser.add_argument(
            "-c", "--config", dest="name", help="Name of config to use", required=True
        )
        parser.add_argument(
            "-w",
            "--websites",
            nargs="+",
            dest="websites",
            help="List of websites to block in the format url1 url2 url3...",
            default=[],
        )
        parser.add_argument(
            "-f",
            "--filters",
            nargs="+",
            dest="filters",
            help="List of urls and filter terms to filter out in the format url1,filter1,filter2 url2,filter1...",
            default=[],
        )
        parser.add_argument(
            "-a",
            "--apps",
            nargs="+",
            dest="apps",
            help="List of paths to apps to filter out in the format path1 path2 path3...",
            default=[],
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
        args = parser.parse_args()
        return args

    def _add_subconfig(self, config: dict):
        p_config = self._read_config()
        p_config.update({config["name"]: config})
        self._write_config(p_config)

    def run(self):
        args = self.parse_args()
        if args.update:
            if args.create:
                method = "add"
            elif args.remove:
                method = "subtract"
            else:
                raise Exception("-n or -r flag must be passed along with -u flag")
            config = self.update_config(
                args.name, args.websites, args.filters, args.apps, method
            )
            self._add_subconfig(config)
        elif args.create:
            config = self.create_config(
                args.name, args.websites, args.filters, args.apps
            )
            self._add_subconfig(config)
        elif args.remove:
            config = self.get_config(args.name)
            self.remove_config(args.name)
        else:
            config = self.get_config(args.name)
        return config


if __name__ == "__main__":
    config = Config()
    print(config.run())

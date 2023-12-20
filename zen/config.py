from argparse import ArgumentParser
from plugins import Websites, UrlFilters, Programs
import json
import os

dir_name = os.path.dirname(os.path.dirname(os.path.abspath("__file__")))
BASE_CONFIG_PATH = f"{dir_name}/configs/base_config.json"


class Config:
    def __init__(self, fields: list):
        self.base_path = BASE_CONFIG_PATH
        self.fields = [field(idx + 1) for idx, field in enumerate(fields)]
        if not os.path.exists(BASE_CONFIG_PATH):
            self._write_config({})

    def _read_config(self) -> dict:
        with open(self.base_path, "r") as fp:
            return json.load(fp)

    def _write_config(self, content) -> None:
        with open(self.base_path, "w") as fp:
            json.dump(content, fp)

    def create_config(self, name: str, fields: list) -> dict:
        fields = [
            field.process_field(values) for field, values in zip(self.fields, fields)
        ]
        return {
            name: {
                field.name.lower(): values for field, values in zip(self.fields, fields)
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

    def update_config(self, name: str, fields: list, method: str):
        config = self.get_config(name)
        fields = [
            field.process_field(values) for field, values in zip(self.fields, fields)
        ]
        for field, values in zip(self.fields, fields):
            fn = getattr(field, f"update_{method}")
            config[field.name.lower()] = field.post_update(
                fn(
                    field.pre_update(config[field.name.lower()]),
                    field.pre_update(values),
                )
            )
        return {name: config}

    def parse_args(self):
        parser = ArgumentParser()
        parser.add_argument(
            "-c", "--config", dest="name", help="Name of config to use", required=True
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
        for field in self.fields:
            parser.add_argument(
                f"-f{field.idx}",
                f"--{field.name.lower()}",
                dest=field.name.lower(),
                nargs="+",
                help=field.help,
                default=field.default,
            )
        args = parser.parse_args()
        return args

    def _add_subconfig(self, config):
        base_config = self._read_config()
        base_config.update(config)
        self._write_config(base_config)

    def run(self):
        args = self.parse_args()
        if args.update:
            method = "subtract" if args.remove else "add"
            config = self.update_config(
                args.name,
                [getattr(args, field.name.lower()) for field in self.fields],
                method,
            )
            self._add_subconfig(config)
        elif args.create:
            config = self.create_config(
                args.name, [getattr(args, field.name.lower()) for field in self.fields]
            )
            self._add_subconfig(config)
        elif args.remove:
            config = self.get_config(args.name)
            self.remove_config(args.name)

        return config


if __name__ == "__main__":
    config = Config([Websites, UrlFilters, Programs])
    print(config.run())
from configparser import ConfigParser
from argparse import ArgumentParser
import os
import re

BASE_CONFIG_PATH = f'{os.getcwd()}/configs/base_config.ini'

class Config:

    def __init__(self):
        if not os.path.exists(BASE_CONFIG_PATH):
            self._write_config() 
        self.config = ConfigParser()
        self.config.read(BASE_CONFIG_PATH)

    def _write_config(self):
        with open(BASE_CONFIG_PATH, 'w') as configfile:
            self.config.write(configfile)

    def create_config(self, name:str, websites:str):
        websites = websites.split(',')
        websites = [website.strip() for website in websites if re.match(r'^https?://', website)]
        self.config[name] = {
            'websites': ','.join(websites)
        }
        self._write_config()

    def remove_config(self, name):
        if name in self.config.sections():
            self.config.remove_section(name)
            self._write_config()
        else:
            raise Exception(f'Config with name {name} does not exist')

    def get_config(self, name):
        if name in self.config.sections():
            return self.config[name]['websites'].split(',')
        else:
            raise Exception(f'Config with name {name} does not exist')

    def parse_args(self):
        parser = ArgumentParser()
        parser.add_argument('-c', '--config', dest='config_name', help='Name of config to use', required=True)
        parser.add_argument('-w', '--websites', dest='websites', help='Comma separated list of websites to scrape')
        parser.add_argument('-n', '--new', dest='create', action='store_true', help='Create new config')
        parser.add_argument('-r', '--remove', dest='remove', action='store_true', help='Remove config')
        args = parser.parse_args()
        return args

    def run(self):
        args = self.parse_args()
        if args.create:
            self.create_config(args.config_name, args.websites)
            return self.get_config(args.config_name)
        else:
            config = self.get_config(args.config_name)
            if args.remove:
                self.remove_config(args.config_name)
            return config


if __name__ == '__main__':
    config = Config()
    print(config.run())


    

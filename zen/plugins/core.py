import os
import re
import psutil
from time import sleep
from threading import Thread
from datetime import datetime, timedelta
import logging

class Field:
    def __init__(self, idx: int):
        self.name = "Name"
        self.help = "Help goes here"
        self.required = False
        self.default = []
        self.idx = idx
        self.config = None
        self.block_type = "w"
        self.block_m = {'w': 'whitelist', 'b': 'blacklist'}
        self.time = 2

    @staticmethod
    def process_field(values: list):
        return [value.strip() for value in values]

    def update_add(self, l1, l2):
        return list(set(l1 + l2))

    def update_subtract(self, l1, l2):
        return list(set([e for e in l1 if e not in l2]))

    def pre_update(self, field):
        return field

    def post_update(self, field):
        return field

    def load_config(self, config) -> None:
        self.config = config

    def is_present(self, flow) -> bool:
        return False

    def pre_block(self):
        pass

    def _check_interception(self, flow) -> bool:
        is_present = self.is_present(flow)
        if (self.block_type == 'w' and not is_present) or (self.block_type == 'b' and is_present):
            return True, flow
        else: return False, flow


class Websites(Field):
    def __init__(self, idx: int):
        super().__init__(idx)
        self.name = "Websites"
        self.help = "List of websites to block in the format url1 url2 url3..."

    @staticmethod
    def process_field(values: list):
        return [value.strip() for value in values if re.match(r"^https?://", value)]

    def is_present(self, flow):
        if any([url in flow.request.pretty_url for url in self.config]):
            return True


class Programs(Field):
    def __init__(self, idx: int):
        super().__init__(idx)
        self.name = "Programs"
        self.help = "List of programs to block in the format path1 path2 path3..."

    @staticmethod
    def process_field(values: list):
        return [value.strip() for value in values if os.path.exists(value.strip())]
    
    def pre_block(self):
        Thread(target=self.kill_process_by_path, args=(self.config))
        

    def kill_process_by_path(self, target_paths):
        """Kill a process if its executable path matches the target path."""
        st = datetime.now()
        while st + timedelta(minutes=self.time) < datetime.now():
            for process in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    process_path = process.info['exe']
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    # Handle exceptions that may occur when accessing process information
                    continue

                if process_path and any(target_path in process_path for target_path in target_paths):
                    print(f"Killing process {process.info['name']} (PID {process.info['pid']})")
                    try:
                        os.kill(process.info['pid'], 9)  # Send SIGKILL signal
                    except OSError as e:
                        print(f"Error killing process: {e}")
            sleep(1)


class UrlFilters(Field):
    def __init__(self, idx: int):
        super().__init__(idx)
        self.name = "UrlFilters"
        self.help = (
            "List of url filters to block in the format filter1 filter2 filter3..."
        )

    @staticmethod
    def process_field(values: list):
        d_filters = {}
        filters = list(map(lambda x: [x.split(",")[0], x.split(",")[1:]], values))
        for url, filter in filters:
            if url in d_filters:
                d_filters[url].extend(filter)
            else:
                d_filters[url] = filter
        return d_filters

    def pre_update(self, field):
        res = []
        for w, fs in field.items():
            for f in fs:
                res.append(f"{w},{f}")
        return res

    def post_update(self, field):
        return self.process_field(field)

    def is_present(self, flow) -> bool:
        url = flow.request.pretty_url
        for k,vs in self.config.items():
            for v in vs:
                if k in url and v in url:
                    return True

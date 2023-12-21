import os
import re


class Field:
    def __init__(self, idx: int):
        self.name = "Name"
        self.help = "Help goes here"
        self.required = False
        self.default = []
        self.idx = idx
        self.config = None
        self.field_type = "bool"
        self.block_type = "whitelist"

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

    def filter(self, flow) -> bool:
        return False

    def _check_interception(self, flow) -> bool:
        to_block = self.filter(flow)
        if to_block and self.block_type == "blacklist" or (not to_block) and self.block_type == "whitelist":
            return True
        else: return False


class Websites(Field):
    def __init__(self, idx: int):
        super().__init__(idx)
        self.name = "Websites"
        self.help = "List of websites to block in the format url1 url2 url3..."

    @staticmethod
    def process_field(values: list):
        return [value.strip() for value in values if re.match(r"^https?://", value)]

    def filter(self, flow):
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

    def filter(self, flow) -> bool:
        url = flow.request.pretty_url
        for k,vs in self.config.items():
            for v in vs:
                if k in url and v in url:
                    return True

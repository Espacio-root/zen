import os
import re


class Field:
    def __init__(self, idx: int):
        self.name = "Name"
        self.help = "Help goes here"
        self.required = False
        self.default = []
        self.idx = idx

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


class Websites(Field):
    def __init__(self, idx: int):
        super().__init__(idx)
        self.name = "Websites"
        self.help = "List of websites to block in the format url1 url2 url3..."

    @staticmethod
    def process_field(values: list):
        return [value.strip() for value in values if re.match(r"^https?://", value)]


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

class Catalog:
    SEARCH_LIMIT = 10

    def __init__(self):
        self.sizes = {}   # name -> size
        self.tags = {}    # name -> {field: value}

    def add_file(self, name: str, size: int) -> bool:
        if name in self.sizes:
            return False
        self.sizes[name] = size
        self.tags[name] = {}
        return True

    def search_files(self, prefix: str):
        hits = [(n, s) for n, s in self.sizes.items() if n.startswith(prefix)]
        hits.sort(key=lambda ns: (-ns[1], ns[0]))
        return ["%s(%d)" % (n, s) for n, s in hits[:self.SEARCH_LIMIT]]

    def set_tag(self, name: str, field: str, value: str) -> str:
        if name in self.tags:
            self.tags[name][field] = value
        return ""

    def scan_tags(self, name: str, prefix: str) -> str:
        fields = self.tags.get(name, {})
        chosen = sorted((f, v) for f, v in fields.items() if f.startswith(prefix))
        return ", ".join("%s(%s)" % (f, v) for f, v in chosen)

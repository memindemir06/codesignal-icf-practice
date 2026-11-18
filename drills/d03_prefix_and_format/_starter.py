class Catalog:
    def __init__(self):
        pass

    def add_file(self, name: str, size: int) -> bool:
        # -> True added | False name taken
        raise NotImplementedError

    def search_files(self, prefix: str):
        # -> top 10 ['name(size)'], size desc then name asc
        raise NotImplementedError

    def set_tag(self, name: str, field: str, value: str) -> str:
        # -> "" always
        raise NotImplementedError

    def scan_tags(self, name: str, prefix: str) -> str:
        # -> "field(value), field(value)" sorted by field asc | ""
        raise NotImplementedError

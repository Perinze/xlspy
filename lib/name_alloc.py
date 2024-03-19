
class NameAllocator:
    def __init__(self):
        self.count = 0

    def next(self):
        self.count += 1
        return self.count

    def next_with_name(self, name: str):
        self.count += 1
        return f"{name}.{self.count}"

UNALLOC = 0
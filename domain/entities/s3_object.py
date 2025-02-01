class S3Object:
    def __init__(self, key: str, size: int, last_modified):
        self.key = key
        self.size = size
        self.last_modified = last_modified

    def __repr__(self):
        return f"S3Object(key={self.key}, size={self.size}, last_modified={self.last_modified})"

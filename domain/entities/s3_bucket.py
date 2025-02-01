from datetime import datetime


class S3Bucket:
    def __init__(self, name: str, creation_date: datetime = None):
        self.name = name
        self.creation_date = creation_date or datetime.utcnow()

    def __repr__(self):
        return f"S3Bucket(name={self.name}, creation_date={self.creation_date})"

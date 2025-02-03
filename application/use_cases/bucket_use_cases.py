from domain.interfaces.s3_repository import S3Repository
from domain.entities.s3_bucket import S3Bucket
from typing import List


class BucketUseCases:
    def __init__(self, repository: S3Repository):
        self.repository = repository

    def get_buckets(self) -> List[S3Bucket]:
        return self.repository.list_buckets()

    def create_bucket(self, bucket_name: str) -> bool:
        return self.repository.create_bucket(bucket_name)

    def delete_bucket(self, bucket_name: str) -> bool:
        return self.repository.delete_bucket(bucket_name)

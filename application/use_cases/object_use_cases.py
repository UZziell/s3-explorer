from domain.repositories.s3_repository import S3Repository
from domain.entities.s3_object import S3Object
from typing import List


class ObjectUseCases:
    def __init__(self, repository: S3Repository):
        self.repository = repository

    def get_objects(self, bucket_name: str) -> List[S3Object]:
        return self.repository.list_objects(bucket_name)

    def upload_object(self, bucket_name: str, file_path: str) -> bool:
        return self.repository.upload_object(bucket_name, file_path)

    def delete_object(self, bucket_name: str, object_key: str) -> bool:
        return self.repository.delete_object(bucket_name, object_key)

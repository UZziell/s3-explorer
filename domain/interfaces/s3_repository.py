from abc import ABC, abstractmethod
from typing import List
from domain.entities.s3_bucket import S3Bucket
from domain.entities.s3_object import S3Object


class S3Repository(ABC):
    @abstractmethod
    def list_buckets(self) -> List[S3Bucket]:
        pass

    @abstractmethod
    def create_bucket(self, bucket_name: str) -> bool:
        pass

    @abstractmethod
    def delete_bucket(self, bucket_name: str) -> bool:
        pass

    @abstractmethod
    def list_objects(self, bucket_name: str) -> List[S3Object]:
        pass

    @abstractmethod
    def upload_object(self, bucket_name: str, file_path: str) -> bool:
        pass

    @abstractmethod
    def generate_presigned_url(
        self, bucket_name: str, file_name: str, expiration
    ) -> str:
        pass

    @abstractmethod
    def delete_object(self, bucket_name: str, object_key: str) -> bool:
        pass

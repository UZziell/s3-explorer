import boto3
import logging
from io import BytesIO
from botocore.exceptions import ClientError
from typing import List
from datetime import datetime
from domain.interfaces.s3_repository import S3Repository
from domain.entities.s3_bucket import S3Bucket
from domain.entities.s3_object import S3Object


class Boto3S3Repository(S3Repository):
    def __init__(self):
        self.s3_client = boto3.client(
            service_name="s3",
            aws_access_key_id="test",
            aws_secret_access_key="test",
            endpoint_url="http://localhost:4566",
        )

    def list_buckets(self) -> List[S3Bucket]:
        try:
            response = self.s3_client.list_buckets()
            return [
                S3Bucket(bucket["Name"], bucket.get("CreationDate", datetime.utcnow()))
                for bucket in response.get("Buckets", [])
            ]
        except ClientError as e:
            logging.error(f"Error listing buckets: {e}")
            return []

    def create_bucket(self, bucket_name: str) -> bool:
        try:
            self.s3_client.create_bucket(Bucket=bucket_name)
            return True
        except ClientError as e:
            logging.error(f"Error creating bucket: {e}")
            return False

    def delete_bucket(self, bucket_name: str) -> bool:
        try:
            self.s3_client.delete_bucket(Bucket=bucket_name)
            return True
        except ClientError as e:
            logging.error(f"Error deleting bucket {bucket_name}: {e}")
            return False

    def list_objects(self, bucket_name: str) -> List[S3Object]:
        try:
            response = self.s3_client.list_objects_v2(Bucket=bucket_name)
            return [
                S3Object(obj["Key"], obj["Size"], obj["LastModified"])
                for obj in response.get("Contents", [])
            ]
        except ClientError as e:
            logging.error(f"Error listing objects in {bucket_name}: {e}")
            return []

    def put_object(self, bucket_name: str, file_path: str) -> bool:
        try:
            object_key = file_path.split("/")[-1]
            with open(file_path, "rb") as file_data:
                self.s3_client.put_object(
                    Bucket=bucket_name, Key=object_key, Body=file_data
                )
            return True
        except ClientError as e:
            logging.error(f"Error uploading object {file_path}: {e}")
            return False

    def generate_presigned_url(
        self, bucket_name: str, file_name: str, expiration=3600
    ) -> str:
        try:
            url = self.s3_client.generate_presigned_url(
                "put_object",
                Params={"Bucket": bucket_name, "Key": file_name},
                ExpiresIn=expiration,
            )
            return url
        except ClientError as e:
            logging.error(f"Error generating presigned URL {file_name}: {e}")
            return None

    def delete_object(self, bucket_name: str, object_key: str) -> bool:
        try:
            self.s3_client.delete_object(Bucket=bucket_name, Key=object_key)
            return True
        except ClientError as e:
            logging.error(f"Error deleting object {object_key} from {bucket_name}: {e}")
            return False

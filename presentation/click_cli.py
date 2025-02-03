import click
from domain.use_cases.bucket_use_cases import BucketUseCases
from domain.use_cases.object_use_cases import ObjectUseCases
from adapters.boto3_s3_repository import Boto3S3Repository

repository = Boto3S3Repository()
bucket_use_cases = BucketUseCases(repository)
object_use_cases = ObjectUseCases(repository)


@click.version_option("0.1.0", prog_name="s3cli")
@click.group()
def cli():
    pass


@cli.command()
def list_buckets():
    """Lists all buckets"""
    for bucket in bucket_use_cases.get_buckets():
        click_print(bucket.name, bucket.creation_date)


@cli.command()
@click.option("--bucket", help="Name of the bucket to create", required=True)
def create_bucket(bucket):
    """Create a bucket"""
    bucket_use_cases.create_bucket(bucket_name=bucket)


@cli.command()
@click.option("--bucket", help="Name of the bucket to delete", required=True)
def delete_bucket(bucket):
    """Delete a bucket"""
    if click.confirm(f"Delete bucket '{bucket}'?"):
        if bucket_use_cases.delete_bucket(bucket_name=bucket):
            click.echo(f"Bucket '{bucket}' deleted")
        else:
            click.echo(f"Could NOT delete bucket '{bucket}'")
    else:
        click.echo("Delete Aborted!")


@cli.command()
@click.option("--bucket", help="Name of the bucket to list objects", required=True)
def list_objects(bucket):
    """Lists all objects in a bucket"""
    for obj in object_use_cases.get_objects(bucket):
        click_print(obj.key, obj.last_modified)


@cli.command()
@click.option("--bucket", help="Name of the bucket to create object in", required=True)
@click.option(
    "--key",
    type=click.Path(
        exists=True,
        readable=True,
        file_okay=True,
    ),
    help="Path to file that should be uploaded to bucket",
    required=True,
)
def put_object(bucket, key):
    """Put an object into bucket"""
    if object_use_cases.put_object(bucket, key):
        click.echo(f"Object '{key}' uploaded to '{bucket}'.")
    else:
        click.echo("Upload failed!")


@cli.command()
@click.option(
    "--bucket", help="Name of the bucket to delete object from", required=True
)
@click.option("--key", help="Key of the object to delete", required=True)
def delete_object(bucket, key):
    """Delete an object from bucket"""
    if click.confirm(f"Delete object '{key}'?"):
        if object_use_cases.delete_object(bucket, key):
            click.echo(f"object '{key}' deleted")
        else:
            click.echo(f"Could NOT delete object '{bucket,key}'")
    else:
        click.echo("Delete Aborted!")


def click_print(item, datetime):
    click.echo(f"{item.ljust(50)} Creation time: {datetime}")


if __name__ == "__main__":
    cli()

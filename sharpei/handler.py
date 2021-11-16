import glob
import io
from os import path
from typing import Union
import logging
import mimetypes

from watchdog import events
import boto3


s3_client = boto3.client('s3')
logger = logging.getLogger("sharpei")


class SharpeiEventHandler(events.FileSystemEventHandler):
    def __init__(
        self,
        *,
        base_path: str,
        bucket: str,
        base_key: str,
        s3_args: dict,
    ) -> None:
        """
        :param base_path: Base local path to generate S3 keys relative to
        :param bucket: S3 bucket name
        :param base_key: Base to be prepended to S3 keys
        :param s3_args: Additional args to be passed into S3 calls
        """
        self.base_path = base_path
        self.bucket = bucket
        self.base_key = base_key
        self.s3_args = s3_args

    def _relative_s3_filename(self, filename: str) -> str:
        if filename.startswith(self.base_path):
            filename = filename[len(self.base_path):]
        filename = filename.replace("\\", "/")
        if filename.startswith("/"):
            filename = filename[1:]
        return filename

    def s3_upload(self, file_path: str):
        # Save file in memory.
        with open(file_path, "rb") as f:
            file_buf = io.BytesIO(f.read())

        upload_key = self.base_key + self._relative_s3_filename(file_path)
        logger.info(f"Upload {file_path} to s3://{self.bucket}/{upload_key}")
        extra_args = self.s3_args.copy()
        mimetype, _ = mimetypes.guess_type(file_path)
        if mimetype:
            extra_args["ContentType"] = mimetype
        s3_client.upload_fileobj(Fileobj=file_buf, Bucket=self.bucket, Key=upload_key, ExtraArgs=extra_args)

    def on_any_event(self, event: events.FileSystemEvent):
        logger.debug(event)

    def on_moved(self, event: events.FileSystemMovedEvent):
        # Move is actioned as a copy and then delete
        cp_src_key = self.base_key + self._relative_s3_filename(event.src_path)
        cp_target_key = self.base_key + self._relative_s3_filename(event.dest_path)
        logger.info(f"Move-copy s3://{self.bucket}/{cp_src_key} to s3://{self.bucket}/{cp_target_key}")
        s3_client.copy_object(
            Bucket=self.bucket,
            CopySource={
                'Bucket': self.bucket,
                'Key': cp_src_key,
            },
            Key=cp_target_key,
            **self.s3_args,
        )

        rm_key = self.base_key + self._relative_s3_filename(event.src_path)
        logger.info(f"Move-delete s3://{self.bucket}/{rm_key}")
        s3_client.delete_object(
            Bucket=self.bucket,
            Key=rm_key,
        )

    def on_created(self, event: Union[events.FileCreatedEvent, events.DirCreatedEvent]):
        if event.is_directory:
            for file in glob.glob(path.join(event.src_path, '**'), recursive=True):
                if path.isfile(file):
                    self.s3_upload(file)
        else:
            self.s3_upload(event.src_path)

    def on_deleted(self, event: Union[events.FileDeletedEvent, events.DirDeletedEvent]):
        if event.is_directory:
            for file in glob.glob(path.join(event.src_path, '**'), recursive=True):
                if path.isfile(file):
                    s3_client.delete_object(
                        Bucket=self.bucket,
                        Key=self.base_key + self._relative_s3_filename(file)
                    )
        else:
            s3_client.delete_object(
                Bucket=self.bucket,
                Key=self.base_key + self._relative_s3_filename(event.src_path)
            )

    def on_modified(self, event: Union[events.FileModifiedEvent, events.DirModifiedEvent]):
        if not event.is_directory:
            self.s3_upload(event.src_path)

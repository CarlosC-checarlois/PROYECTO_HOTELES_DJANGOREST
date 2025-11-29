
import os
import uuid
import boto3
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile

def subir_pdf_a_s3(pdf_bytes: bytes, filename: str) -> str:
    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )

    s3.put_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=filename,
        Body=pdf_bytes,
        ContentType="application/pdf",
    )

    return f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{filename}"


def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )



def subir_imagen_habitacion_a_s3(file_obj: UploadedFile) -> str:
    """
    Sube la imagen recibida (UploadedFile) a S3 y devuelve la URL pública.
    No usa ACLs para evitar el error AccessControlListNotSupported.
    """
    if not file_obj:
        return ""

    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )

    bucket = settings.AWS_STORAGE_BUCKET_NAME

    # extensión original (.jpg, .png, etc.)
    _, ext = os.path.splitext(file_obj.name)
    ext = ext or ".png"

    # ruta tipo: imagenes/carlos/<uuid>.ext
    key = f"imagenes/carlos/{uuid.uuid4().hex}{ext}"

    s3.upload_fileobj(
        Fileobj=file_obj,
        Bucket=bucket,
        Key=key,
        ExtraArgs={
            "ContentType": file_obj.content_type or "image/png",
        },
    )

    url = f"https://{bucket}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"
    return url



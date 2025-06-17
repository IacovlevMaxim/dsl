from src.utils.image_metadata import metadata_prefix
from src.utils.variable_type import *


def map_audio_field(field_name: str) -> str:
    """Maps metadata field names for audio files."""
    return field_name  # Audio files use the field name directly.


def map_image_field(field_name: str) -> str:
    """Maps metadata field names for image files."""
    if ":" in field_name:
        return field_name
    return f"{metadata_prefix(field_name)}:{field_name}"  # Prefix for image metadata.


def map_video_field(field_name: str) -> str:
    """Maps metadata field names for video files."""
    mp4_keys = {
        "title": "©nam",
        "artist": "©ART",
        "album": "©alb",
        "genre": "©gen",
        "description": "desc"
    }
    if field_name not in mp4_keys:
        raise AttributeError(f"Metadata field '{field_name}' does not exist for video files.")
    return mp4_keys[field_name]


def map_pdf_field(field_name: str) -> str:
    """Maps metadata field names for PDF files."""
    if not field_name.startswith("/"):
        field_name = f"/{field_name}"
    return field_name


variable_type_to_map_field = {
    VariableType.AUDIO_FILE: map_audio_field,
    VariableType.IMAGE_FILE: map_image_field,
    VariableType.VIDEO_FILE: map_video_field,
    VariableType.PDF_FILE: map_pdf_field
}
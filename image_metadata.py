
field_to_prefix = {
    "FileName": "File",
    "Directory": "File",
    "FileSize": "File",
    "FileModifyDate": "File",
    "FileAccessDate": "File",
    "FileInodeChangeDate": "File",
    "FilePermissions": "File",
    "FileType": "File",
    "FileTypeExtension": "File",
    "MIMEType": "File",
    "ExifByteOrder": "File",
    "ImageWidth": "PNG",
    "ImageHeight": "PNG",
    "BitDepth": "PNG",
    "ColorType": "PNG",
    "Compression": "PNG",
    "Filter": "PNG",
    "Interlace": "PNG",
    "Palette": "PNG",
    "Artist": "PNG",  # Note: "Artist" appears in both PNG and EXIF, but we take PNG as per the given list
    "Title": "PNG",  # Similarly, "Title" appears in both PNG and XMP, but PNG comes first
    "XMPToolkit": "XMP",
    "Keywords": "IPTC",
    "ApplicationRecordVersion": "IPTC",
    "YCbCrPositioning": "EXIF",
    "Copyright": "EXIF",
    "ImageSize": "Composite",
    "Megapixels": "Composite",
}


def metadata_prefix(field):
    return field_to_prefix.get(field, "XMP")

from enum import Enum


class VariableType(Enum):
    UNKNOWN = 0
    NUMBER = 1
    STRING = 2
    AUDIO_FILE = 3
    BOOLEAN = 4
    IMAGE_FILE = 5
    type_names = {
        UNKNOWN: "unknown",
        NUMBER: "number",
        STRING: "string",
        AUDIO_FILE: "audio file",
        BOOLEAN: "boolean",
        IMAGE_FILE: "image file"
    }

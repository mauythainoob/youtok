from typing import TypeAlias, Union

from pocketbase.models import Record

PocketBaseValueOptions: TypeAlias = Union[str, float, int, bool]

# Collection record
TiktokCollectionRecord: TypeAlias = Record
MetadataCollectionRecord: TypeAlias = Record
CompilationRecord: TypeAlias = Record
VideoCollectionRecord: TypeAlias = Record


# Tiktok collection fields
TiktokRecordId: TypeAlias = str
TiktokRecordVideoId: TypeAlias = str

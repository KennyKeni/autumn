from enum import StrEnum

DEFAULT_FILE_TOOL_GROUP = "DefaultFileToolGroup"


class PartitionDbStatus(StrEnum):
    ACTIVE = "active"
    DISABLED = "disabled"
    DELETED = "deleted"


class PartitionFileDbStatus(StrEnum):
    PENDING = "pending"
    EMBEDDING = "embedding"
    ACTIVE = "active"
    FAILED = "failed"


class PartitionFileToolType(StrEnum):
    SUMMARY = "summary"
    VECTOR = "vector"


# PartitionFileToolTypeDescription: Dict[PartitionFileToolType, str] = {
#     PartitionFileToolType.SUMMARY: (
#         f"Search for specific concepts, methods, techniques, or technical details in {file_name.split('.')[0]}. "
#         f"Use this for questions about specific algorithms, implementations, formulas, or technical concepts. "
#         f"Examples: quantization methods, model architectures, specific equations."
#     ),
#     PartitionFileToolType.VECTOR: "",
# }

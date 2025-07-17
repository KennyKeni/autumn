from enum import Enum


class PartitionDbStatus(str, Enum):
    ACTIVE = "active"
    DISABLED = "disabled"
    DELETED = "deleted"

class PartitionFileDbStatus(str, Enum):
    PENDING = "pending"
    EMBEDDING = "embedding" 
    ACTIVE = "active"
    FAILED = "failed"


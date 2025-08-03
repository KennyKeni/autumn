from llama_index.core.vector_stores import (
    FilterOperator,
    MetadataFilter,
    MetadataFilters,
)


# TODO This shit is ass btw
def get_partition_file_llamaindex_filter(partition_file_id: str):
    return MetadataFilters(
        filters=[
            MetadataFilter(
                key="partition_file_id",
                value=partition_file_id,
                operator=FilterOperator.EQ,
            )
        ]
    )

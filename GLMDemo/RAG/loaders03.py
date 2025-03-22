from langchain_community.document_loaders import JSONLoader

def create_metadata(record: dict, metadata: dict) -> dict:
    metadata['sender_name'] = record.get('sender_name')
    metadata['timestamp_ms'] = record.get('timestamp_ms')
    return metadata

loader = JSONLoader(
    file_path='test.json',
    jq_schema='.messages[]',
    metadata_func=create_metadata,
    text_content=False
)


data = loader.load()

print(data)
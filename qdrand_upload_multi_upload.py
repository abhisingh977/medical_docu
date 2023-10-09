from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    OptimizersConfigDiff,
)
import json
from tqdm import tqdm
import os

start_directory = "/home/abhishek/abhi/medical/json_files"

url = os.environ["URL"]
api_key = os.environ["API_KEY"]

client = QdrantClient(
    url=url,
    api_key=api_key,
)

count = 0
client.recreate_collection(
    collection_name="medical_docu",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    optimizers_config=OptimizersConfigDiff(
        indexing_threshold=0,
    ),
)
json_files = []

# # Walk through the directory tree using os.walk
for root, dirs, files in os.walk(start_directory):
    for file in files:
        # Check if the file has a .pdf extension
        if file.endswith(".json"):
            # Construct the full path to the PDF file
            json_path = os.path.join(root, file)
            json_files.append(json_path)


# Print the list of PDF file paths
for i in tqdm(range(len(json_files))):
    points = []
    try:
        with open(json_files[i], "r") as f:
            data = json.load(f)
    except:
        print(json_files[i])

    for t in data:
        points.append(
            PointStruct(
                id=count,
                payload={
                    "text": t["text"],
                    "page_no": str(t["page_no"]),
                    "filename": t["filename"],
                },
                vector=t["embedding"],
            )
        )
        count += 1
    # The maximum number of points to upsert in each batch
    batch_size = 1000

    # Calculate the number of batches needed
    num_batches = len(points) // batch_size + 1

    # Initialize a starting index
    start_index = 0

    # Assume you have a client.upsert function that takes a collection name and a list of points
    while start_index < len(points):
        # Calculate the end index for the current batch
        end_index = start_index + batch_size

        # Get the batch of points
        batch = points[start_index:end_index]

        # Upsert the batch into the collection
        client.upsert(collection_name="medical_docu", points=batch)

        # Update the start index for the next batch
        start_index = end_index

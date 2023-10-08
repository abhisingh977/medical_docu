# from qdrant_client import QdrantClient
# from qdrant_client.models import (
#     OptimizersConfigDiff,
# )

# client = QdrantClient(
#     url="https://9a61774e-dd62-4dcd-a475-9a1ccfcf89b6.us-east4-0.gcp.cloud.qdrant.io:6333",
#     api_key="ddrUQecTjYVIc39ckHemRSZP5sfiyWq1fLxvJpzUxFg-2PdeKbV1tw",
# )

# client.update_collection(
#     collection_name="medical_docu",
#     optimizer_config=OptimizersConfigDiff(
#         indexing_threshold=10000
#     )
# )
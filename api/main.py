from fastapi import FastAPI
import uvicorn
from typing import List, Dict
from sentence_transformers import SentenceTransformer
# Create an instance of the FastAPI class
app = FastAPI()

# Define a simple endpoint
@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

retriever = SentenceTransformer("/model/")

@app.post("/get_embedding_from_input/")
async def convert_string_to_list(input_text_json: Dict[str, str]) -> List[List[float]]:
    # Assuming the input string is comma-separated
    input_text = input_text_json["input_text"]
    encoded_query = retriever.encode(
            input_text
        ).tolist()  # generate embeddings for the question

    return [encoded_query]

# This block will allow you to run this app using the command: uvicorn main:app --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
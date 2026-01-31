import os
from typing import List, Dict
from dotenv import load_dotenv
from langchain_community.document_loaders import CSVLoader
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_postgres import PGVector
from langchain_core.documents import Document

load_dotenv()

# --- Configuration ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
from supabase import create_client, Client
from sentence_transformers import SentenceTransformer

supabase: Client = create_client(SUPABASE_URL, os.getenv("SUPABASE_KEY"))
model = SentenceTransformer('all-MiniLM-L6-v2') 

class RAGSystem:
    def __init__(self):
        self.dims = 384
        
    def embed_text(self, text: str) -> List[float]:
        """Convert text to vector."""
        return model.encode(text).tolist()

    def ingest_csv(self, file_content: str, metadata: Dict):
        """Parse CSV content and save embeddings."""
        # Simple splitting by line
        lines = file_content.split('\n')
        header = lines[0]
        
        chunk_batch = []
        for line in lines[1:]:
            if not line.strip(): continue
            
            # Create a meaningful text representation
            # e.g. "Employee: Alice, Role: CEO"
            text_representation = f"Context: {metadata.get('type', 'General')}\nData: {header}\nValues: {line}"
            
            vector = self.embed_text(text_representation)
            
            chunk_batch.append({
                "content": text_representation,
                "metadata": metadata,
                "embedding": vector
            })
            
        # Bulk Insert
        if chunk_batch:
            data = supabase.table("documents").insert(chunk_batch).execute()
        return len(chunk_batch)

    def clean_project_data(self, project_id: str):
        """Remove all documents for a specific project to prevent stale data."""
        try:
            # We assume metadata contains 'project_id'
            # Note: This requires the metadata column to be queried appropriately. 
            # In Supabase filter, we access jsonb fields using ->> operator string matching
            supabase.table("documents").delete().eq("metadata->>project_id", str(project_id)).execute()
            print(f"Cleaned old vectors for project: {project_id}")
        except Exception as e:
            print(f"Error cleaning project data: {e}")

    def retrieve(self, query: str, limit: int = 3) -> List[str]:
        """Find relevant context for a query."""
        query_vector = self.embed_text(query)

        
        params = {
            "query_embedding": query_vector,
            "match_threshold": 0.0, # Debug: Lowered to catch any match
            "match_count": limit
        }
        
        try:
            res = supabase.rpc("match_documents", params).execute()
            return [item['content'] for item in res.data]
        except Exception as e:
            print(f"RAG Retrieval Error: {e}")
            return []

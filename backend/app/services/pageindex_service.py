from pageindex import PageIndexClient
from app.config import PAGEINDEX_API_KEY

pi_client = PageIndexClient(api_key=PAGEINDEX_API_KEY)


def upload_document(file_path: str):
    result = pi_client.submit_document(file_path)
    return result["doc_id"]


def get_tree(doc_id: str):
    result = pi_client.get_tree(doc_id, node_summary=True)
    return result.get("result", [])


def check_status(doc_id: str):
    return pi_client.get_document(doc_id).get("status")
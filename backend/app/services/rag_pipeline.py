import json

# from regex import search
# from sklearn import tree
from app.services.llm_service import call_llm_json, call_llm_text
from app.services.redis_service import get_cache, set_cache
from app.utils.logger import logger
from app.services.reranker import rerank
from backend.app.main import query
from backend.app.main import query


# 🔥 STEP 1: COMPRESS TREE
def compress_tree(nodes):
    out = []
    for n in nodes:
        entry = {
            "node_id": n["node_id"],
            "title": n["title"],
            "page": n.get("page_index", "?"),
            "summary": n.get("text", "")[:120]  # reduced size
        }
        if n.get("nodes"):
            entry["children"] = compress_tree(n["nodes"])
        out.append(entry)
    return out


# 🔥 STEP 2: FLATTEN TREE
def flatten_tree(nodes):
    result = []
    for n in nodes:
        result.append(n)
        if n.get("nodes"):
            result.extend(flatten_tree(n["nodes"]))
    return result


# 🔥 STEP 3: KEYWORD FILTER (huge cost reduction)
def keyword_filter(query, nodes, limit=25):
    query_words = query.lower().split()

    scored = []
    for n in nodes:
        text = (n.get("title", "") + " " + n.get("text", "")).lower()

        score = sum(1 for w in query_words if w in text)

        if score > 0:
            scored.append((score, n))

    scored.sort(reverse=True, key=lambda x: x[0])

    return [n for _, n in scored[:limit]]


# 🔥 STEP 4: LLM TREE SEARCH (OPTIMIZED PROMPT)
def llm_tree_search(query, nodes):
    prompt = f"""
You are a retrieval system.

Select the most relevant node_ids for answering the query.

Query:
{query}

Nodes:
{json.dumps(nodes)}

Rules:
- Return ONLY JSON
- No explanation
- Select top 3–5 relevant nodes

Output:
{{
  "node_list": ["id1", "id2"]
}}
"""

    response = call_llm_json(prompt)

    try:
        return json.loads(response)
    except:
        return {"node_list": []}


# 🔥 STEP 5: FIND NODES
def find_nodes(tree, ids):
    result = []
    for node in tree:
        if node["node_id"] in ids:
            result.append(node)
        if node.get("nodes"):
            result.extend(find_nodes(node["nodes"], ids))
    return result


# 🔥 STEP 6: GENERATE ANSWER (SHORT CONTEXT)
def generate_answer(query, nodes):
    context = "\n\n".join([
        f"{n['title']} (Page {n.get('page_index')})\n{n.get('text', '')[:500]}"
        for n in nodes
    ])

    prompt = f"""
Answer ONLY using the context.

Question:
{query}

Context:
{context}

Rules:
- Be precise
- Cite section titles
"""

    return call_llm_text(prompt)


# 🔥 FINAL PIPELINE
def run_rag(query, tree,doc_id):
    cache_key = f"{doc_id}:{query.strip().lower()}"

    cached = get_cache(cache_key)
    if cached:
        logger.info("Cache hit")
        return cached

    logger.info("Processing query")

    # Step 1: flatten
    flat_nodes = flatten_tree(tree)

# Step 2: keyword filter
    filtered_nodes = keyword_filter(query, flat_nodes)

# 🔥 Step 3: rerank (NEW)
    reranked_nodes = rerank(query, filtered_nodes)

# Step 4: compress only top nodes
    compressed_nodes = compress_tree(reranked_nodes)

# Step 5: LLM selection
    search = llm_tree_search(query, compressed_nodes)

    node_ids = search.get("node_list", [])

# Step 6: final nodes
    selected_nodes = find_nodes(tree, node_ids)
    # Generate answer
    answer = generate_answer(query, selected_nodes)

    set_cache(cache_key, answer)
    return answer
from sentence_transformers import CrossEncoder

# lightweight model
model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')


def rerank(query, nodes, top_k=5):
    if not nodes:
        return []

    pairs = []

    for n in nodes:
        text = n.get("title", "") + " " + n.get("text", "")[:300]
        pairs.append((query, text))

    scores = model.predict(pairs)

    scored_nodes = list(zip(scores, nodes))
    scored_nodes.sort(reverse=True, key=lambda x: x[0])

    return [node for _, node in scored_nodes[:top_k]]
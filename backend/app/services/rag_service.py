from app.rag.retriever import retrieve
from app.services.llm_service import generate_response
from app.services.query_rewriter import rewrite_query


def generate_rag_response(question: str, history: list | None = None) -> dict:
    search_queries = rewrite_query(
        question,
        history
    )

    all_results = []

    specific_terms = [
        "wireless headphones",
        "mechanical keyboard",
        "wireless mouse",
    ]

    for search_query in search_queries:
        print("REWRITTEN QUERY:", search_query)

        top_k = 5

        if any(
            term in search_query.lower()
            for term in specific_terms
        ):
            top_k = 2

        query_results = retrieve(
            search_query,
            top_k=top_k
        )

        all_results.extend(query_results)

    results = []
    seen_texts = set()

    for result in all_results:
        print("QUERY:", search_query)
        print("SOURCE:", result["source"])
        print("DISTANCE:", result["distance"])
        print("TEXT:", result["text"])
        print("--------------------")
        if result["text"] not in seen_texts:
            results.append(result)
            seen_texts.add(result["text"])

    if not results:
        return {
            "response": "I couldn't find relevant information in the store knowledge base.",
            "sources": []
        }

    context_parts = []

    for result in results:
        context_parts.append(
            f"Source: {result['source']}\n"
            f"{result['text']}"
        )

    context = "\n\n".join(context_parts)

    history_text = ""

    if history:
        recent_messages = history[-6:]

        history_text = "\n".join(
            f"{item.sender}: {item.text}"
            for item in recent_messages
        )

    prompt = f"""
Answer the customer's question using only the store information below.

Use the conversation history only to understand what the customer is referring to.

Do not invent store information.
If the answer is not contained in the provided information,
say that you do not have enough information.

Conversation history:
{history_text if history_text else "No previous conversation."}

Store information:
{context}

Customer question:
{question}
"""

    answer = generate_response(prompt)

    best_distance = results[0]["distance"]

    sources = []

    for result in results:
        if result["distance"] <= best_distance + 0.05:
            source = result["source"]

            if source not in sources:
                sources.append(source)

    return {
        "response": answer,
        "sources": sources
    }
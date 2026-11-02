import json

from app.services.llm_service import generate_response


QUERY_REWRITE_SYSTEM_PROMPT = """
You rewrite customer support questions into short, clear search queries
for retrieving information from an online store knowledge base.

Use the conversation history when the current question refers to something
mentioned earlier.

Rules:
- Preserve the original meaning.
- Resolve pronouns such as "it", "that", "this one", or "the other one"
  using the conversation history when possible.
- Resolve pronouns such as "it", "they", "that", "this one", and "those"
  using the most recently discussed product or products from history.
- If the previous answer identified a single product, prefer that product
  even if the customer uses an ambiguous plural pronoun.
- Until the customer explicitly asks for a different product, assume they are
  referring to the most recently discussed product or products.
- If the customer asks for a specific detail about a product and that detail is
  not present in the currently retrieved product information, rewrite the query
  to search the wider knowledge base for that exact detail.
- If the customer asks for multiple different pieces of information,
  create one search query for each piece of information.
- Do not broaden a question about one product into a query about all products.
- Do not answer the question.
- Do not invent information.
- Make the query explicit and retrieval-friendly.
- Return only the rewritten query.
- Keep it concise.
- Return ONLY valid JSON in this format:

{
  "queries": [
    "search query 1",
    "search query 2"
  ]
}

For a simple question, return only one query.
"""


def rewrite_query(question: str, history: list | None = None) -> list[str]:
    history_text = ""

    if history:
        recent_messages = history[-6:]

        history_text = "\n".join(
            f"{item.sender}: {item.text}"
            for item in recent_messages
        )

    prompt = f"""
Conversation history:
{history_text if history_text else "No previous conversation."}

Current customer question:
{question}
"""

    raw_response = generate_response(
        prompt,
        system_prompt=QUERY_REWRITE_SYSTEM_PROMPT
    )

    try:
        result = json.loads(raw_response)

        queries = result.get("queries", [])

        if queries:
            return queries

    except json.JSONDecodeError:
        pass

    return [question]
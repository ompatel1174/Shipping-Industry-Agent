"""
Fuel Agent – Orchestrates the full query workflow.

1. Receives user natural language query
2. Searches vector DB for relevant table schemas
3. Sends schemas + query to Groq (LLaMA) to generate SQL
4. Executes SQL and returns results
5. Optionally performs calculations
6. Generates a final human-readable response
"""

import json
import re
from groq import Groq
from app.config import settings
from app.tools import vector_store, sql_executor, calculator, doc_retriever
from app.context_manager import ContextManager

# Initialize ContextManager
context_manager = ContextManager()


def _get_client():
    """Create a Groq client."""
    return Groq(api_key=settings.GROQ_API_KEY)


SYSTEM_PROMPT = """You are FuelAgent, an AI assistant specialized in maritime shipping emissions data.
You help users query and analyze fuel consumption, carbon emissions, voyage performance, and CII ratings.

You have access to a PostgreSQL database with the following capabilities:
- Search for relevant table schemas
- Generate and execute SQL queries
- Perform calculations on results

RULES:
1. Always generate valid PostgreSQL SQL (not MySQL).
2. Only generate SELECT statements. Never generate INSERT, UPDATE, DELETE, DROP, or ALTER.
3. Use proper column names from the schema provided.
4. When asked for rankings or top results, always use ORDER BY with LIMIT.
5. For year-based filtering, use the 'year' column.
6. When calculations are needed beyond SQL (percentages, comparisons, derived KPIs), describe them clearly.
7. Always explain your answer clearly and concisely.
8. If you show tabular data, format it neatly.
9. When you generate SQL, wrap it in a ```sql code block.
10. If the user query is ambiguous, ask for clarification.
"""

MODEL = "llama-3.3-70b-versatile"

def process_query(user_query: str, chat_history: list | None = None):
    """
    Process a natural language query through the full agent workflow with streaming.
    Yields dictionaries containing:
    - {'sql': ...}
    - {'data': ..., 'columns': ...}
    - {'chunk': ...}
    - {'error': ...}
    """
    try:
        # --------------------------------------------------
        # Step 0: Context Awareness & Follow-up Detection
        # --------------------------------------------------
        chat_history = chat_history or []
        classification = context_manager.classify_query(user_query, chat_history)
        
        # Reformulate the question to be standalone (for SQL/Vector search)
        standalone_query = context_manager.reformulate_question(user_query, chat_history)

        # --------------------------------------------------
        # Step 1: Handle META (Conversational Follow-ups)
        # --------------------------------------------------
        if classification == "META":
            client = _get_client()
            
            # Get the last assistant message and its context
            last_assistant_msg = next((msg for msg in reversed(chat_history) if msg.get("role") in ["assistant", "model"]), None)
            
            answer_prompt = f"""
            The user is asking a conversational follow-up: "{user_query}"
            
            Based on our previous discussion:
            "{last_assistant_msg.get('content', 'No previous content') if last_assistant_msg else 'No previous context'}"
            
            Please provide a detailed explanation, summary, or further details as requested.
            Do NOT generate SQL. Just talk to the user based on the existing context.
            """
            
            messages_meta = [{"role": "system", "content": SYSTEM_PROMPT}]
            # Add context for the conversation (last 5 turns)
            for msg in chat_history[-10:]:
                role = "assistant" if msg.get("role") == "model" else msg.get("role")
                messages_meta.append({"role": role, "content": msg.get("content")})
            messages_meta.append({"role": "user", "content": answer_prompt})
            
            completion = client.chat.completions.create(
                model=MODEL,
                messages=messages_meta,
                temperature=0.3,
                max_tokens=2048,
                stream=True
            )
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    yield {"chunk": chunk.choices[0].delta.content}
            return

        # --------------------------------------------------
        # Step 1.5: Handle DOCS (Agent Documentation)
        # --------------------------------------------------
        if classification == "DOCS":
            # Search the agent documentation
            doc_context = doc_retriever.retrieve_agent_docs(standalone_query)
            
            client = _get_client()
            answer_prompt = f"""
            The user is asking about the seaQL agent: "{user_query}"
            
            Based on the following documentation:
            {doc_context}
            
            Please provide a friendly and detailed answer based ONLY on the documentation provided.
            """
            
            messages_docs = [{"role": "system", "content": SYSTEM_PROMPT}]
            messages_docs.append({"role": "user", "content": answer_prompt})
            
            completion = client.chat.completions.create(
                model=MODEL,
                messages=messages_docs,
                temperature=0.3,
                max_tokens=2048,
                stream=True
            )
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    yield {"chunk": chunk.choices[0].delta.content}
            return

        # --------------------------------------------------
        # Step 2: Vector search for relevant schemas (New/Standalone Query)
        # --------------------------------------------------
        schema_matches = vector_store.search(standalone_query, top_k=2)
        schema_context = "\n\n".join(
            f"--- Table: {m['table_name']} ---\n{m['ddl']}\n\n{m['schema_text']}"
            for m in schema_matches
        )

        # --------------------------------------------------
        # Step 3: Ask Groq (LLaMA) to generate SQL
        # --------------------------------------------------
        client = _get_client()
        
        sql_prompt = f"""Based on the following database schemas, generate a PostgreSQL SELECT query to answer the user's question.
        
        DATABASE SCHEMAS:
        {schema_context}
        
        USER QUESTION (Standalone): {standalone_query}
        
        Respond with ONLY the SQL query, no explanation. Wrap it in ```sql``` code fences.
        If the question cannot be answered with the available tables, respond with: CANNOT_ANSWER: <reason>
        """

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.append({"role": "user", "content": sql_prompt})

        sql_response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.1,
            max_tokens=1024,
        )

        sql_text = sql_response.choices[0].message.content.strip()

        if sql_text.startswith("CANNOT_ANSWER"):
            yield {"chunk": sql_text.replace("CANNOT_ANSWER:", "").strip()}
            return

        sql_query = _extract_sql(sql_text)
        if not sql_query:
            yield {"chunk": "I couldn't generate a valid SQL query for your question. Could you rephrase it?"}
            return

        yield {"sql": sql_query}

        # --------------------------------------------------
        # Step 4: Execute the SQL query
        # --------------------------------------------------
        exec_result = sql_executor.execute(sql_query)

        if not exec_result["success"]:
            yield {"error": exec_result["error"]}
            yield {"chunk": f"I encountered an error executing the query: {exec_result['error']}"}
            return

        yield {"data": exec_result["rows"], "columns": exec_result["columns"]}

        # --------------------------------------------------
        # Step 5: Generate final human-readable response (STREAMING)
        # --------------------------------------------------
        data_summary = json.dumps(exec_result["rows"][:20], indent=2, default=str)
        row_count = exec_result["row_count"]

        answer_prompt = f"""The user asked: "{user_query}"
        (Standalone reformulated query: "{standalone_query}")
        
        I ran this SQL query:
        ```sql
        {sql_query}
        ```
        
        The query returned {row_count} row(s). Here are the results (first 20 rows):
        {data_summary}
        
        Please provide a clear, well-formatted answer to the user's question based on these results.
        IMPORTANT: DO NOT include the SQL query code block or phrases like "These results are based on the query:" in your response. 
        The SQL query is already displayed to the user in a separate UI component. Focus purely on answering the question with the provided data.
        """

        messages_answer = [{"role": "system", "content": SYSTEM_PROMPT}]
        if chat_history:
             for msg in chat_history[-10:]:
                role = "assistant" if msg.get("role") == "model" else msg.get("role")
                messages_answer.append({"role": role, "content": msg.get("content")})
        
        messages_answer.append({"role": "user", "content": answer_prompt})

        completion = client.chat.completions.create(
            model=MODEL,
            messages=messages_answer,
            temperature=0.3,
            max_tokens=2048,
            stream=True
        )

        for chunk in completion:
            if chunk.choices[0].delta.content:
                yield {"chunk": chunk.choices[0].delta.content}

    except Exception as e:
        yield {"error": str(e)}
        yield {"chunk": f"An unexpected error occurred: {str(e)}"}


def _extract_sql(text: str) -> str | None:
    """Extract SQL query from markdown code fences."""
    # Try to extract from ```sql ... ``` blocks
    pattern = r"```sql\s*(.*?)\s*```"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Try generic code block
    pattern = r"```\s*(.*?)\s*```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # If the entire text looks like SQL (starts with SELECT), use it directly
    if text.upper().strip().startswith("SELECT"):
        return text.strip()

    return None

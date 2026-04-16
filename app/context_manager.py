import os
from groq import Groq
from typing import List, Dict
from app.config import settings

class ContextManager:
    """
    Handles conversation history and question reformulation to make
    the agent context-aware.
    """

    def __init__(self, client: Groq = None):
        if client:
            self.client = client
        else:
            self.client = Groq(api_key=settings.GROQ_API_KEY)

    def classify_query(self, question: str, history: List[Dict[str, str]]) -> str:
        """
        Classifies the query as 'DATA' (requires SQL), 'META' (conversational follow-up),
        or 'DOCS' (questions about the agent itself/workflow/documentation).
        """
        # Removed the 'if not history: return "DATA"' shortcut to allow classification of initial queries as DOCS if appropriate.
        history_text = ""
        # Keep last 6 messages (3 turns) for classification context
        for msg in history[-6:]:
            role = "User" if msg.get("role") == "user" else "Assistant"
            content = msg.get("content", "")
            history_text += f"{role}: {content[:200]}...\n"

        prompt = f"""You are an assistant that classifies shipping industry queries for the seaQL agent.
Your goal is to decide if the "Current Question" needs new data from a database (SQL), is a conversational follow-up, or is asking about the agent itself (SeaQL agent, its workflow, roles, responsibilities, or capabilities).

Classification Categories:
1. DATA: Requires searching for new information, specific metrics, or vessel data not fully covered in the immediate last response.
2. META: Asking to "explain further", "give more details", "elaborate", "summarize that", or similar conversational follow-ups about the last answer.
3. DOCS: Asking about "What is seaQL?", "What are your roles?", "How do you work?", "What is your workflow?", "What can you do?", or anything related to the agent's internal documentation.

Chat History:
{history_text}

Current Question: {question}

Return ONLY the word 'DATA', 'META', or 'DOCS'.
Classification:"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant", # Faster model for classification
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )
            classification = response.choices[0].message.content.strip().upper()
            if "DOCS" in classification:
                return "DOCS"
            elif "META" in classification:
                return "META"
            else:
                return "DATA"
        except Exception:
            return "DATA"

    def reformulate_question(self, question: str, history: List[Dict[str, str]]) -> str:
        """
        Use LLM to rewrite a context-dependent question into a standalone one.
        Ensures awareness of the latest 5 turns (up to 10 messages).
        """
        if not history:
            return question

        # Use exactly last 10 messages for 5 full turns of context awareness
        history_to_process = history[-10:]

        history_text = ""
        for msg in history_to_process:
            role = "User" if msg.get("role") == "user" else "Assistant"
            content = msg.get("content", "")
            history_text += f"{role}: {content}\n"

        prompt = f"""You are a query pre-processor for a shipping analyst agent.
Your task is to rewrite the "Current Question" into a "Standalone Question" that preserves all context from the "Chat History".

Guidelines:
- Resolve all pronouns (it, that, its, they, those).
- If the user asks for "more details" or "explain further", rewrite it to specify WHAT should be explained from the previous context.
- If the question is already standalone, return it exactly as is.
- Keep the standalone question concise.
- Do NOT answer the question. Only rewrite it.

Chat History:
{history_text}

Current Question:
{question}

Standalone Question:"""
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
            )
            reformulated = response.choices[0].message.content.strip()
            return reformulated if reformulated else question
        except Exception:
            return question

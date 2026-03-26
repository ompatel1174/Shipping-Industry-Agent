"""
Tool: Document Retriever
Retrieves relevant information from the seaQL Agent documentation (PDF).
"""

from app.tools.vector_store import search_agent_docs

def retrieve_agent_docs(query: str) -> str:
    """
    Search for information about the seaQL agent, its roles, responsibilities, 
    workflow, and capabilities from the official documentation.
    
    Args:
        query: The user's question about the agent.
        
    Returns:
        A string containing relevant content from the documentation.
    """
    results = search_agent_docs(query, top_k=3)
    
    if not results:
        return "No relevant information found in the documentation."
    
    response = "Found the following information in the agent documentation:\n\n"
    for res in results:
        content = res["content"]
        page = res["metadata"].get("page", "N/A")
        response += f"--- Page {page} ---\n{content}\n\n"
        
    return response

# To make it compatible with the agent's tool system, we might need to export it.
# Assuming the agent uses a list of functions.

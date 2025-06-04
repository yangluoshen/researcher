import os
import json
import httpx
from typing import Any, Dict, List, Optional
from langchain_core.messages import AnyMessage, AIMessage, HumanMessage


def get_research_topic(messages: List[AnyMessage]) -> str:
    """
    Get the research topic from the messages.
    """
    # check if request has a history and combine the messages into a single string
    if len(messages) == 1:
        research_topic = messages[-1].content
    else:
        research_topic = ""
        for message in messages:
            if isinstance(message, HumanMessage):
                research_topic += f"User: {message.content}\n"
            elif isinstance(message, AIMessage):
                research_topic += f"Assistant: {message.content}\n"
    return research_topic


async def search_web(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search the web using SearXNG or fallback search engines.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        
    Returns:
        List of search results with title, url, and content
    """
    # Check for custom SearXNG instance from environment
    custom_searxng = os.getenv("SEARXNG_URL")
    
    # Default SearXNG instances (you can run your own instance or use public ones)
    searxng_instances = []
    if custom_searxng:
        searxng_instances.append(custom_searxng)
    
    # Add public instances as fallback
    searxng_instances.extend([
        "https://searx.be",
        "https://search.sapti.me", 
        "https://searx.tiekoetter.com",
        "https://searx.prvcy.eu",
        "https://search.bus-hit.me"
    ])
    
    for instance in searxng_instances:
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                params = {
                    "q": query,
                    "format": "json",
                    "categories": "general",
                    "engines": os.getenv("SEARCH_ENGINES", "google,bing,duckduckgo"),
                    "safesearch": "0",
                    "time_range": ""
                }
                
                response = await client.get(f"{instance}/search", params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    results = []
                    
                    for result in data.get("results", [])[:max_results]:
                        results.append({
                            "title": result.get("title", ""),
                            "url": result.get("url", ""),
                            "content": result.get("content", ""),
                            "engine": result.get("engine", "searxng")
                        })
                    
                    if results:
                        print(f"Successfully retrieved {len(results)} results from {instance}")
                        return results
                        
        except Exception as e:
            print(f"SearXNG instance {instance} failed: {e}")
            continue
    
    # Fallback to DuckDuckGo instant answers
    print("Falling back to DuckDuckGo instant answers...")
    try:
        return await fallback_duckduckgo_search(query, max_results)
    except Exception as e:
        print(f"Fallback search failed: {e}")
        return await emergency_fallback_search(query, max_results)


async def fallback_duckduckgo_search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Fallback search using DuckDuckGo instant answer API.
    Note: This is a simple fallback and may not return full web results.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            params = {
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            }
            
            response = await client.get("https://api.duckduckgo.com/", params=params)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                # Get abstract if available
                if data.get("Abstract"):
                    results.append({
                        "title": data.get("Heading", query),
                        "url": data.get("AbstractURL", "https://duckduckgo.com/"),
                        "content": data.get("Abstract", ""),
                        "engine": "duckduckgo"
                    })
                
                # Get related topics
                for topic in data.get("RelatedTopics", [])[:max_results-1]:
                    if isinstance(topic, dict) and topic.get("Text"):
                        results.append({
                            "title": topic.get("Text", "")[:100] + "...",
                            "url": topic.get("FirstURL", "https://duckduckgo.com/"),
                            "content": topic.get("Text", ""),
                            "engine": "duckduckgo"
                        })
                
                if results:
                    return results[:max_results]
                
    except Exception as e:
        print(f"DuckDuckGo search failed: {e}")
    
    # If DuckDuckGo also fails, use emergency fallback
    return await emergency_fallback_search(query, max_results)


async def emergency_fallback_search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Emergency fallback when all search engines fail.
    Returns a placeholder result that indicates search failure.
    """
    return [{
        "title": f"Search unavailable for: {query}",
        "url": "https://duckduckgo.com/?q=" + query.replace(" ", "+"),
        "content": f"Unable to fetch live search results for '{query}'. All search engines are currently unavailable. The AI will provide an answer based on its training data, but it may not include the most recent information.",
        "engine": "fallback"
    }]


def resolve_urls(search_results: List[Dict[str, Any]], id: int) -> Dict[str, str]:
    """
    Create a map of original URLs to shortened URLs with unique identifiers.
    
    Args:
        search_results: List of search results with 'url' field
        id: Unique identifier for this search batch
        
    Returns:
        Dictionary mapping original URLs to shortened URLs
    """
    resolved_map = {}
    
    for idx, result in enumerate(search_results):
        original_url = result.get("url", "")
        if original_url and original_url not in resolved_map:
            # Create a shortened URL reference
            short_url = f"[{id}-{idx}]"
            resolved_map[original_url] = short_url
    
    return resolved_map


def insert_citation_markers(text, citations_list):
    """
    Inserts citation markers into a text string based on start and end indices.

    Args:
        text (str): The original text string.
        citations_list (list): A list of dictionaries, where each dictionary
                               contains 'start_index', 'end_index', and
                               'segments' (list of citation segments).

    Returns:
        str: The text with citation markers inserted.
    """
    # Sort citations by end_index in descending order to avoid index shifting
    sorted_citations = sorted(
        citations_list, key=lambda c: (c["end_index"], c["start_index"]), reverse=True
    )

    modified_text = text
    for citation_info in sorted_citations:
        end_idx = citation_info["end_index"]
        marker_to_insert = ""
        for segment in citation_info["segments"]:
            marker_to_insert += f" [{segment['label']}]({segment['value']})"
        
        # Insert the citation marker at the original end_idx position
        modified_text = (
            modified_text[:end_idx] + marker_to_insert + modified_text[end_idx:]
        )

    return modified_text


def create_citations_from_search_results(search_results: List[Dict[str, Any]], text: str) -> List[Dict[str, Any]]:
    """
    Create citation objects from search results for the generated text.
    
    Args:
        search_results: List of search results
        text: The generated text content
        
    Returns:
        List of citation dictionaries
    """
    citations = []
    
    # For simplicity, create one citation covering the entire text
    # In a more sophisticated implementation, you could analyze which parts
    # of the text correspond to which sources
    if search_results:
        segments = []
        for i, result in enumerate(search_results):
            segments.append({
                "label": result.get("title", f"Source {i+1}")[:50] + ("..." if len(result.get("title", "")) > 50 else ""),
                "short_url": f"[{i}]",
                "value": result.get("url", "")
            })
        
        citations.append({
            "start_index": 0,
            "end_index": len(text),
            "segments": segments
        })
    
    return citations


def get_citations(response, resolved_urls_map):
    """
    Extracts and formats citation information from a language model's response.
    This is a legacy function kept for compatibility.
    
    Args:
        response: The response object from the language model
        resolved_urls_map: A mapping of original URLs to shortened URLs.

    Returns:
        List of citation dictionaries
    """
    # This function is kept for backward compatibility
    # Real citation creation should use create_citations_from_search_results
    return []

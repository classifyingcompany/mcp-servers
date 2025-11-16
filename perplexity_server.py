from typing import Any, List
import httpx
import json
from mcp.server.fastmcp import FastMCP
import os
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("perplexity-browse")

# Get Perplexity API key from environment
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_API_BASE = "https://api.perplexity.ai"

async def make_perplexity_request(messages: List[dict], model: str = "sonar-pro") -> dict[str, Any] | None:
    """Make a request to Perplexity API with proper error handling."""
    if not PERPLEXITY_API_KEY:
        return {"error": "PERPLEXITY_API_KEY environment variable not set"}
    
    # Debug: Log API key status (without revealing the key)
    print(f"DEBUG: API key present: {bool(PERPLEXITY_API_KEY)}")
    print(f"DEBUG: API key length: {len(PERPLEXITY_API_KEY) if PERPLEXITY_API_KEY else 0}")
    
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Updated payload to match Perplexity API latest format
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 2000,
        "temperature": 0.2,
        "top_p": 0.9,
        "return_citations": True,
        "return_images": False,
        "return_related_questions": False
    }
    
    # Debug: Log request details
    print(f"DEBUG: Making request to: {PERPLEXITY_API_BASE}/chat/completions")
    print(f"DEBUG: Model: {model}")
    print(f"DEBUG: Messages count: {len(messages)}")
    print(f"DEBUG: Payload keys: {list(payload.keys())}")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{PERPLEXITY_API_BASE}/chat/completions",
                headers=headers,
                json=payload
            )
            
            # Debug response
            print(f"DEBUG: Response status: {response.status_code}")
            print(f"DEBUG: Response headers: {dict(response.headers)}")
            
            if not response.is_success:
                error_text = response.text
                print(f"DEBUG: Error response body: {error_text}")
                return {
                    "error": f"API Error {response.status_code}: {error_text}",
                    "status_code": response.status_code
                }
            
            response_json = response.json()
            print(f"DEBUG: Response JSON keys: {list(response_json.keys()) if response_json else 'None'}")
            
            return response_json
            
        except httpx.HTTPStatusError as e:
            error_detail = f"HTTP {e.response.status_code}: {e.response.text}"
            print(f"DEBUG: HTTP Status Error: {error_detail}")
            return {"error": error_detail}
        except httpx.RequestError as e:
            error_detail = f"Request error: {str(e)}"
            print(f"DEBUG: Request Error: {error_detail}")
            return {"error": error_detail}
        except Exception as e:
            error_detail = f"Unexpected error: {str(e)}"
            print(f"DEBUG: Unexpected Error: {error_detail}")
            return {"error": error_detail}

def format_perplexity_response(response_data: dict) -> str:
    """Format Perplexity API response into readable text."""
    if "error" in response_data:
        return f"Error: {response_data['error']}"
    
    if "choices" not in response_data or not response_data["choices"]:
        return "Error: No response from Perplexity API"
    
    choice = response_data["choices"][0]
    content = choice["message"]["content"]
    
    # Extract citations if available
    citations = []
    if "citations" in choice.get("message", {}):
        citations = choice["message"]["citations"]
    
    result = f"{content}\n"
    
    if citations:
        result += "\n📚 Sources:\n"
        for i, citation in enumerate(citations, 1):
            result += f"{i}. {citation}\n"
    
    return result

@mcp.tool()
async def test_api_connection() -> str:
    """Test Perplexity API connection and authentication.
    
    Returns diagnostic information about the API setup.
    """
    try:
        # Check API key
        if not PERPLEXITY_API_KEY:
            return "❌ PERPLEXITY_API_KEY environment variable not set"
        
        # Basic info about the key (without revealing it)
        key_info = f"✅ API key present (length: {len(PERPLEXITY_API_KEY)})"
        
        # Test with a very simple request
        simple_messages = [
            {"role": "user", "content": "What is 2+2?"}
        ]
        
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Simple payload
        simple_payload = {
            "model": "sonar-pro",
            "messages": simple_messages,
            "max_tokens": 100
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{PERPLEXITY_API_BASE}/chat/completions",
                    headers=headers,
                    json=simple_payload
                )
                
                if response.is_success:
                    result = response.json()
                    return f"""✅ API Connection Test SUCCESSFUL
{key_info}
✅ Response status: {response.status_code}
✅ Response contains: {list(result.keys())}
✅ Test message response: {result.get('choices', [{}])[0].get('message', {}).get('content', 'No content')[:100]}..."""
                else:
                    return f"""❌ API Connection Test FAILED
{key_info}
❌ Status: {response.status_code}
❌ Error: {response.text}
❌ Headers: {dict(response.headers)}"""
                    
            except Exception as e:
                return f"""❌ API Connection Test FAILED
{key_info}
❌ Exception: {str(e)}
❌ Exception type: {type(e).__name__}"""
                
    except Exception as e:
        return f"❌ Test failed with error: {str(e)}"

@mcp.tool()
async def web_search(query: str, model: str = "sonar-pro") -> str:
    """Search the web using Perplexity AI with real-time information.
    
    Args:
        query: Search query
        model: Perplexity model to use (default: llama-3.1-sonar-small-128k-online)
    """
    try:
        messages = [
            {
                "role": "user",
                "content": f"Search for: {query}"
            }
        ]
        
        response = await make_perplexity_request(messages, model)
        return format_perplexity_response(response)
    
    except Exception as e:
        return f"Error performing web search: {str(e)}"

@mcp.tool()
async def get_current_news(topic: str = "", model: str = "sonar-pro") -> str:
    """Get current news and latest information on a specific topic.
    
    Args:
        topic: News topic or subject (optional, gets general news if empty)
        model: Perplexity model to use (default: llama-3.1-sonar-small-128k-online)
    """
    try:
        if topic:
            query = f"Latest news and updates about {topic} today"
        else:
            query = "Latest breaking news and current events today"
        
        messages = [
            {
                "role": "user", 
                "content": query
            }
        ]
        
        response = await make_perplexity_request(messages, model)
        return format_perplexity_response(response)
    
    except Exception as e:
        return f"Error getting current news: {str(e)}"

@mcp.tool()
async def research_topic(topic: str, depth: str = "comprehensive", model: str = "sonar-pro") -> str:
    """Research a topic in-depth with current information.
    
    Args:
        topic: Topic to research
        depth: Research depth - 'quick', 'standard', 'comprehensive' (default: 'comprehensive')
        model: Perplexity model to use (default: llama-3.1-sonar-large-128k-online for research)
    """
    try:
        depth_prompts = {
            "quick": f"Provide a quick overview of {topic} with the most current information available.",
            "standard": f"Research and explain {topic} with current data, key facts, and recent developments.",
            "comprehensive": f"Conduct comprehensive research on {topic}. Include current statistics, recent developments, expert opinions, different perspectives, and provide a detailed analysis with the latest information available."
        }
        
        prompt = depth_prompts.get(depth, depth_prompts["comprehensive"])
        
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        response = await make_perplexity_request(messages, model)
        return format_perplexity_response(response)
    
    except Exception as e:
        return f"Error researching topic: {str(e)}"

@mcp.tool()
async def fact_check(claim: str, model: str = "sonar-pro") -> str:
    """Fact-check a claim using current sources and information.
    
    Args:
        claim: Claim or statement to fact-check
        model: Perplexity model to use (default: llama-3.1-sonar-large-128k-online)
    """
    try:
        messages = [
            {
                "role": "user",
                "content": f"Fact-check this claim using current, reliable sources: '{claim}'. Provide evidence for or against this claim, cite your sources, and give a clear assessment of its accuracy."
            }
        ]
        
        response = await make_perplexity_request(messages, model)
        return format_perplexity_response(response)
    
    except Exception as e:
        return f"Error fact-checking: {str(e)}"

@mcp.tool()
async def get_stock_info(symbol: str, model: str = "sonar-pro") -> str:
    """Get current stock information and market data.
    
    Args:
        symbol: Stock symbol (e.g., AAPL, GOOGL, TSLA)
        model: Perplexity model to use (default: llama-3.1-sonar-small-128k-online)
    """
    try:
        messages = [
            {
                "role": "user",
                "content": f"Get the current stock price, market data, and recent news for {symbol}. Include current price, daily change, volume, market cap, and any recent significant news or events affecting the stock."
            }
        ]
        
        response = await make_perplexity_request(messages, model)
        return format_perplexity_response(response)
    
    except Exception as e:
        return f"Error getting stock information: {str(e)}"

@mcp.tool()
async def get_weather_forecast(location: str, model: str = "sonar-pro") -> str:
    """Get current weather and forecast for a location.
    
    Args:
        location: City, state/country (e.g., "New York, NY" or "London, UK")
        model: Perplexity model to use (default: llama-3.1-sonar-small-128k-online)
    """
    try:
        messages = [
            {
                "role": "user",
                "content": f"Get the current weather conditions and 7-day forecast for {location}. Include temperature, humidity, precipitation, wind, and any weather warnings or advisories."
            }
        ]
        
        response = await make_perplexity_request(messages, model)
        return format_perplexity_response(response)
    
    except Exception as e:
        return f"Error getting weather forecast: {str(e)}"

@mcp.tool()
async def compare_products(products: str, criteria: str = "", model: str = "sonar-pro") -> str:
    """Compare products or services using current information and reviews.
    
    Args:
        products: Products to compare (comma-separated)
        criteria: Specific criteria to compare (optional)
        model: Perplexity model to use (default: llama-3.1-sonar-large-128k-online)
    """
    try:
        product_list = [p.strip() for p in products.split(',')]
        
        if criteria:
            query = f"Compare {' vs '.join(product_list)} based on {criteria}. Include current prices, specifications, reviews, and expert opinions."
        else:
            query = f"Compare {' vs '.join(product_list)}. Include current prices, key features, pros and cons, user reviews, and expert recommendations."
        
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]
        
        response = await make_perplexity_request(messages, model)
        return format_perplexity_response(response)
    
    except Exception as e:
        return f"Error comparing products: {str(e)}"

@mcp.tool()
async def get_tech_trends(area: str = "general", model: str = "sonar-pro") -> str:
    """Get current technology trends and developments.
    
    Args:
        area: Technology area (e.g., "AI", "blockchain", "cloud", "mobile", "general")
        model: Perplexity model to use (default: llama-3.1-sonar-large-128k-online)
    """
    try:
        if area.lower() == "general":
            query = "What are the current major technology trends and developments in 2024-2025? Include AI, cloud computing, cybersecurity, and emerging technologies."
        else:
            query = f"What are the current trends and latest developments in {area} technology? Include recent innovations, market changes, and future predictions."
        
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]
        
        response = await make_perplexity_request(messages, model)
        return format_perplexity_response(response)
    
    except Exception as e:
        return f"Error getting tech trends: {str(e)}"

@mcp.tool()
async def get_travel_info(destination: str, travel_type: str = "general", model: str = "sonar-pro") -> str:
    """Get current travel information for a destination.
    
    Args:
        destination: Travel destination
        travel_type: Type of travel info - 'general', 'safety', 'attractions', 'weather', 'requirements'
        model: Perplexity model to use (default: llama-3.1-sonar-small-128k-online)
    """
    try:
        queries = {
            "general": f"Current travel guide for {destination}. Include best time to visit, top attractions, local culture, food, and practical tips.",
            "safety": f"Current travel safety information for {destination}. Include safety ratings, health advisories, and travel warnings.",
            "attractions": f"Top current attractions and activities in {destination}. Include must-see places, experiences, and recent additions.",
            "weather": f"Current weather conditions and climate information for {destination}. Include seasonal weather patterns.",
            "requirements": f"Current travel requirements for {destination}. Include visa requirements, vaccination needs, and entry restrictions."
        }
        
        query = queries.get(travel_type, queries["general"])
        
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]
        
        response = await make_perplexity_request(messages, model)
        return format_perplexity_response(response)
    
    except Exception as e:
        return f"Error getting travel information: {str(e)}"

@mcp.tool()
async def ask_question(question: str, context: str = "", model: str = "sonar-pro") -> str:
    """Ask any question and get an answer with current web information.
    
    Args:
        question: Question to ask
        context: Additional context for the question (optional)
        model: Perplexity model to use (default: llama-3.1-sonar-large-128k-online)
    """
    try:
        if context:
            content = f"Question: {question}\n\nAdditional context: {context}\n\nPlease answer this question using the most current and accurate information available."
        else:
            content = f"Question: {question}\n\nPlease answer this question using the most current and accurate information available."
        
        messages = [
            {
                "role": "user",
                "content": content
            }
        ]
        
        response = await make_perplexity_request(messages, model)
        return format_perplexity_response(response)
    
    except Exception as e:
        return f"Error answering question: {str(e)}"

def main():
    """Initialize and run the Perplexity browsing MCP server."""
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
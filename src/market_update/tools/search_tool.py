from crewai.tools import BaseTool
from typing import Type, List, Dict, Union, Any
from pydantic import BaseModel, Field, validator
from langchain_community.tools import DuckDuckGoSearchRun, DuckDuckGoSearchResults
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
import json

class DuckDuckGoSearchInput(BaseModel):
    """Input schema for DuckDuckGoSearchTool."""
    query: Union[str, dict] = Field(
        ..., 
        description="Your search query (e.g., 'MSFT stock news last 3 days')"
    )
    search_type: str = Field(
        default="detailed",
        description="Use 'basic' for simple results or 'detailed' for more information"
    )
    max_results: int = Field(
        default=20,
        description="Number of results to return"
    )
    output_format: str = Field(
        default="list",
        description="Use 'list' or 'string' format"
    )
    region: str = Field(
        default="all",
        description="Region for search results"
    )
    time_period: str = Field(
        default="d",
        description="'d' for day, 'w' for week, 'm' for month"
    )
    backend: str = Field(
        default="news",
        description="Use 'news' for news articles only"
    )

    @validator('query')
    def validate_query(cls, v):
        if isinstance(v, dict):
            if 'description' in v:
                return v['description']
            elif 'query' in v:
                return v['query']
            raise ValueError("Dictionary must contain 'description' or 'query' key")
        return v

class DuckDuckGoSearchTool(BaseTool):
    name: str = "DuckDuckGo Search"
    description: str = (
        "Search for recent news and information. Input can be a simple search query string or a dictionary. "
        "Example inputs: 'MSFT stock news last 3 days' or {'query': 'MSFT stock news last 3 days', "
        "'search_type': 'detailed', 'time_period': 'd'}"
    )
    args_schema: Type[BaseModel] = DuckDuckGoSearchInput

    def _run(
        self,
        query: Union[str, dict],
        search_type: str = "detailed",
        max_results: int = 20,
        output_format: str = "list",
        region: str = "all",
        time_period: str = "d",
        backend: str = "news"
    ) -> Union[str, List[Dict[str, str]]]:
        """Execute the DuckDuckGo search with the specified parameters."""
        try:
            # Convert the query to string if it's a dictionary
            if isinstance(query, dict):
                if 'description' in query:
                    query = query['description']
                elif 'query' in query:
                    query = query['query']
                else:
                    query = str(query)
            
            if search_type == "basic":
                search = DuckDuckGoSearchRun()
                return search.invoke(str(query))
            else:
                wrapper = DuckDuckGoSearchAPIWrapper(
                    region=region,
                    time=time_period
                )
                
                search = DuckDuckGoSearchResults(
                    api_wrapper=wrapper,
                    backend=backend,
                    output_format=output_format
                )
                
                return search.invoke(str(query))
                
        except Exception as e:
            return f"Error performing search: {str(e)}"

    def _parse_input(self, tool_input: Union[str, dict]) -> dict:
        """Parse various input formats into a standardized dictionary."""
        try:
            # If input is a string, try to parse it as JSON
            if isinstance(tool_input, str):
                try:
                    parsed_input = json.loads(tool_input)
                except json.JSONDecodeError:
                    # If not valid JSON, treat it as a direct query
                    return {"query": tool_input}
            else:
                parsed_input = tool_input

            # Ensure we have a dictionary
            if not isinstance(parsed_input, dict):
                return {"query": str(parsed_input)}

            # Extract and validate parameters
            params = {
                "query": parsed_input.get("query", ""),
                "search_type": parsed_input.get("search_type", "detailed"),
                "max_results": parsed_input.get("max_results", 20),
                "output_format": parsed_input.get("output_format", "list"),
                "region": parsed_input.get("region", "all"),
                "time_period": parsed_input.get("time_period", "d"),
                "backend": parsed_input.get("backend", "news")
            }

            # Handle nested query structure
            if isinstance(params["query"], dict):
                if "description" in params["query"]:
                    params["query"] = params["query"]["description"]
                elif "query" in params["query"]:
                    params["query"] = params["query"]["query"]

            return params

        except Exception as e:
            # If anything goes wrong, return a default configuration
            return {
                "query": str(tool_input),
                "search_type": "detailed",
                "max_results": 20,
                "output_format": "list",
                "region": "all",
                "time_period": "d",
                "backend": "news"
            }
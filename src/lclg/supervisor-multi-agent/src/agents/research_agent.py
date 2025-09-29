"""ResearchAgent for information gathering and reasoning."""

import json
import requests
from typing import Any, Dict, List, Optional
from datetime import datetime
from langchain.tools import BaseTool, tool
from pydantic import BaseModel, Field

from .base_agent import BaseAgent, AgentMessage


class WebSearchInput(BaseModel):
    """Input for web search tool."""
    query: str = Field(description="Search query")


class ResearchAgent(BaseAgent):
    """Agent specialized in research and information gathering."""
    
    def __init__(
        self,
        llm: Optional[Any] = None,
        temperature: float = 0.1,
        model_name: str = "gpt-4",
        api_key: Optional[str] = None
    ):
        super().__init__(
            name="ResearchAgent",
            llm=llm,
            temperature=temperature,
            model_name=model_name,
            api_key=api_key
        )
    
    def _setup_tools(self) -> None:
        """Set up research tools."""
        self.tools = [
            self._create_web_search_tool(),
            self._create_fact_checker_tool(),
            self._create_summarizer_tool(),
            self._create_knowledge_analyzer_tool()
        ]
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the research agent."""
        return """You are a specialized research and information gathering agent. Your expertise includes:

- Web search and information retrieval
- Fact-checking and verification
- Data analysis and synthesis
- Research methodology and best practices
- Source evaluation and credibility assessment
- Information summarization and organization

When conducting research:
1. Use multiple sources to verify information
2. Evaluate source credibility and bias
3. Provide citations and references when possible
4. Distinguish between facts and opinions
5. Identify gaps in available information
6. Present findings in a clear, organized manner

Always be thorough, objective, and transparent about your research process."""
    
    def _get_agent_type(self) -> str:
        """Get the agent type for prompt selection."""
        return "research"
    
    def _create_web_search_tool(self) -> BaseTool:
        """Create a web search tool (mock implementation)."""
        
        @tool("web_search")
        def web_search(query: str) -> str:
            """Perform web search (mock implementation)."""
            # In a real implementation, you would use a search API like:
            # - Google Search API
            # - Bing Search API
            # - SerpAPI
            # - DuckDuckGo API
            
            # Mock search results for demonstration
            mock_results = {
                "artificial intelligence": [
                    {
                        "title": "What is Artificial Intelligence?",
                        "url": "https://example.com/ai-basics",
                        "snippet": "Artificial Intelligence (AI) is the simulation of human intelligence in machines..."
                    },
                    {
                        "title": "AI Applications in Healthcare",
                        "url": "https://example.com/ai-healthcare",
                        "snippet": "AI is revolutionizing healthcare with applications in diagnosis, treatment, and drug discovery..."
                    }
                ],
                "climate change": [
                    {
                        "title": "Climate Change Facts and Figures",
                        "url": "https://example.com/climate-facts",
                        "snippet": "Global temperatures have risen by approximately 1.1°C since pre-industrial times..."
                    },
                    {
                        "title": "Renewable Energy Solutions",
                        "url": "https://example.com/renewable-energy",
                        "snippet": "Solar and wind power are becoming increasingly cost-effective alternatives to fossil fuels..."
                    }
                ]
            }
            
            # Simple keyword matching for demo
            query_lower = query.lower()
            results = []
            
            for topic, search_results in mock_results.items():
                if any(word in query_lower for word in topic.split()):
                    results.extend(search_results)
            
            if not results:
                results = [{
                    "title": f"Search results for: {query}",
                    "url": "https://example.com/search",
                    "snippet": f"Here are some relevant results for your query about {query}..."
                }]
            
            formatted_results = []
            for i, result in enumerate(results[:5], 1):  # Limit to 5 results
                formatted_results.append(
                    f"{i}. {result['title']}\n   URL: {result['url']}\n   {result['snippet']}\n"
                )
            
            return f"Search results for '{query}':\n\n" + "\n".join(formatted_results)
        
        return web_search
    
    def _create_fact_checker_tool(self) -> BaseTool:
        """Create a fact-checking tool."""
        
        @tool("fact_checker")
        def fact_check(statement: str) -> str:
            """Check the veracity of a statement."""
            # This is a simplified fact-checker
            # In production, you would integrate with fact-checking APIs or databases
            
            statement_lower = statement.lower()
            
            # Simple keyword-based fact checking (for demonstration)
            verified_facts = {
                "earth is round": "VERIFIED: The Earth is approximately spherical (oblate spheroid).",
                "water boils at 100": "VERIFIED: Water boils at 100°C (212°F) at standard atmospheric pressure.",
                "sun rises in east": "VERIFIED: The sun appears to rise in the east due to Earth's rotation.",
            }
            
            disputed_facts = {
                "vaccines cause autism": "DISPUTED: Multiple scientific studies have found no link between vaccines and autism.",
                "climate change is a hoax": "DISPUTED: Overwhelming scientific consensus supports human-caused climate change.",
            }
            
            for fact, verification in verified_facts.items():
                if fact in statement_lower:
                    return f"✅ {verification}"
            
            for fact, verification in disputed_facts.items():
                if fact in statement_lower:
                    return f"❌ {verification}"
            
            # Default response for unverified statements
            return f"⚠️  Statement '{statement}' requires further verification. I recommend consulting multiple reliable sources and fact-checking organizations."
        
        return fact_check
    
    def _create_summarizer_tool(self) -> BaseTool:
        """Create a text summarization tool."""
        
        @tool("summarizer")
        def summarize_text(text: str) -> str:
            """Summarize long text content."""
            # Simple extractive summarization (for demonstration)
            # In production, you would use more sophisticated NLP models
            
            sentences = text.split('. ')
            if len(sentences) <= 3:
                return f"Text is already concise:\n{text}"
            
            # Simple heuristic: take first, middle, and last sentences
            summary_sentences = []
            
            # First sentence
            if sentences:
                summary_sentences.append(sentences[0])
            
            # Middle sentence
            if len(sentences) > 2:
                middle_idx = len(sentences) // 2
                summary_sentences.append(sentences[middle_idx])
            
            # Last sentence
            if len(sentences) > 1:
                summary_sentences.append(sentences[-1])
            
            summary = '. '.join(summary_sentences)
            if not summary.endswith('.'):
                summary += '.'
            
            return f"Summary:\n{summary}\n\nOriginal length: {len(text)} characters\nSummary length: {len(summary)} characters"
        
        return summarize_text
    
    def _create_knowledge_analyzer_tool(self) -> BaseTool:
        """Create a tool for analyzing and organizing knowledge."""
        
        @tool("knowledge_analyzer")
        def analyze_knowledge(topic: str) -> str:
            """Analyze and organize knowledge about a topic."""
            # This is a simplified knowledge analyzer
            # In production, you would use knowledge graphs, ontologies, or specialized databases
            
            analysis = {
                "topic": topic,
                "timestamp": datetime.now().isoformat(),
                "key_concepts": [],
                "related_topics": [],
                "knowledge_gaps": [],
                "confidence_level": "medium"
            }
            
            # Simple keyword-based analysis (for demonstration)
            topic_lower = topic.lower()
            
            if "artificial intelligence" in topic_lower or "ai" in topic_lower:
                analysis["key_concepts"] = [
                    "Machine Learning", "Neural Networks", "Deep Learning", 
                    "Natural Language Processing", "Computer Vision"
                ]
                analysis["related_topics"] = [
                    "Machine Learning", "Data Science", "Robotics", 
                    "Cognitive Science", "Ethics in AI"
                ]
                analysis["knowledge_gaps"] = [
                    "Ethical implications", "Bias in AI systems", 
                    "Explainable AI", "AI safety"
                ]
            
            elif "climate" in topic_lower:
                analysis["key_concepts"] = [
                    "Global Warming", "Greenhouse Gases", "Carbon Footprint",
                    "Renewable Energy", "Sustainability"
                ]
                analysis["related_topics"] = [
                    "Environmental Science", "Renewable Energy", 
                    "Carbon Markets", "Climate Policy"
                ]
                analysis["knowledge_gaps"] = [
                    "Long-term climate projections", "Regional impacts",
                    "Mitigation strategies", "Adaptation measures"
                ]
            
            else:
                analysis["key_concepts"] = ["General knowledge", "Basic concepts"]
                analysis["related_topics"] = ["Related fields", "Adjacent topics"]
                analysis["knowledge_gaps"] = ["Specific details", "Recent developments"]
            
            return f"""Knowledge Analysis for '{topic}':

Key Concepts: {', '.join(analysis['key_concepts'])}
Related Topics: {', '.join(analysis['related_topics'])}
Knowledge Gaps: {', '.join(analysis['knowledge_gaps'])}

Confidence Level: {analysis['confidence_level']}
Analysis Time: {analysis['timestamp']}"""
        
        return analyze_knowledge

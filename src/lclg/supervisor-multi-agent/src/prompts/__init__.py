"""Prompt templates for the multi-agent system."""

from .prompts import (
    get_agent_prompt,
    get_task_analysis_prompt,
    get_complex_task_prompt
)

__all__ = [
    "get_agent_prompt", 
    "get_task_analysis_prompt",
    "get_complex_task_prompt"
]

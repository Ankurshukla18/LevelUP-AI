# This file would hold prompt templates for an actual LLM integration.
# e.g. using LangChain or similar.

GENERATE_ROADMAP_PROMPT = """
You are an expert AI coach. Generate a step-by-step roadmap for the following goal:
Goal Name: {name}
Category: {category}
Duration: {weeks} weeks
Current Level: {current_level}
Target Outcome: {target_outcome}
Available Hours/Week: {hours}
"""

ANALYZE_WEEK_PROMPT = """
Analyze the user's progress for this week and provide insights.
...
"""

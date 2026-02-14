"""
Suno Prompt Refiner Agent using OpenAI Function Calling.
Implements a ReAct-style agent that analyzes, refines, and validates prompts.
"""

import os
import json
from openai import OpenAI
from agent_tools import TOOL_DEFINITIONS, execute_tool

SYSTEM_PROMPT = """You are a Suno AI Prompt Specialist. Your job is to take music generation prompts and optimize them for the best results in Suno AI.

## Your Process:
1. First, call analyze_prompt to understand the input
2. Call check_suno_guidelines for relevant aspects (like "arrangement", "mood", "production")
3. Based on analysis, create an improved prompt
4. Call validate_prompt to check your work
5. Return the final refined prompt

## Refinement Guidelines:
- Keep the core musical style and mood intact
- Add specific production terms (warm analog mix, spacious reverb, etc.)
- Include arrangement hints (intro style, dynamics, builds)
- Use effective keywords that Suno understands well
- Keep under 200 words
- Use comma-separated descriptors
- NEVER use negative terms (no, without, don't) - use positive alternatives
- Ensure good category coverage (tempo, mood, instruments, production, arrangement)

After your final validation, respond with ONLY "REFINED PROMPT:" followed by the optimized prompt text."""


def run_refinement_agent(prompt: str, api_key: str = None) -> dict:
    """
    Run the Suno prompt refiner agent using function calling.
    """
    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OpenAI API key required")

    client = OpenAI(api_key=api_key)
    reasoning_steps = []

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Please analyze and refine this Suno music prompt:\n\n{prompt}"}
    ]

    # Allow multiple rounds of function calling
    max_rounds = 10
    final_response = None

    for round_num in range(max_rounds):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
            max_tokens=1000
        )

        message = response.choices[0].message

        # Check if we have tool calls
        if message.tool_calls:
            # Add assistant message with tool calls
            messages.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]
            })

            # Process each tool call
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    arguments = {}

                # Log reasoning step
                reasoning_steps.append({
                    "action": function_name,
                    "input": arguments
                })

                # Execute the tool
                result = execute_tool(function_name, arguments)

                # Log result summary
                try:
                    result_data = json.loads(result)
                    if function_name == "analyze_prompt":
                        reasoning_steps.append({
                            "observation": f"Analysis: {result_data.get('overall_assessment', 'completed')}",
                            "details": f"Categories: {result_data.get('categories_detected', [])}, Issues: {len(result_data.get('issues', []))}"
                        })
                    elif function_name == "validate_prompt":
                        reasoning_steps.append({
                            "observation": f"Validation score: {result_data.get('score', '?')}/10",
                            "details": f"Verdict: {result_data.get('verdict', 'unknown')}"
                        })
                    else:
                        reasoning_steps.append({
                            "observation": f"Retrieved {function_name.replace('_', ' ')} info"
                        })
                except:
                    reasoning_steps.append({
                        "observation": f"Completed {function_name}"
                    })

                # Add tool response
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
        else:
            # No tool calls - this is the final response
            final_response = message.content
            break

    if not final_response:
        # If we exhausted rounds, get final response without tools
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages + [{"role": "user", "content": "Please provide the final refined prompt now. Start with 'REFINED PROMPT:'"}],
            max_tokens=500
        )
        final_response = response.choices[0].message.content

    # Extract the refined prompt
    refined_prompt = final_response
    if "REFINED PROMPT:" in final_response:
        refined_prompt = final_response.split("REFINED PROMPT:")[-1].strip()

    # Clean up any markdown or extra formatting
    refined_prompt = refined_prompt.strip('`"\' \n')

    # Get the final score from reasoning
    score = 7  # default
    for step in reversed(reasoning_steps):
        if "observation" in step and "score:" in step["observation"].lower():
            try:
                score_str = step["observation"].split(":")[1].split("/")[0].strip()
                score = int(float(score_str))
            except:
                pass
            break

    return {
        "refined_prompt": refined_prompt,
        "score": score,
        "reasoning": reasoning_steps
    }


# Keep the simple refine_prompt function for backwards compatibility
def refine_prompt(base_prompt: str, api_key: str = None) -> str:
    """
    Simple wrapper that returns just the refined prompt.
    For the full agent experience with reasoning, use run_refinement_agent().
    """
    result = run_refinement_agent(base_prompt, api_key)
    return result["refined_prompt"]

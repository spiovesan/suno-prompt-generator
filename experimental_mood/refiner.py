"""
Suno Prompt Studio Refiner Agent using OpenAI Function Calling.
Analyzes and refines both Style (audio quality) and Lyrics (meta tags) outputs.
Supports both Jazz mode and Universal mode.
"""

import os
import json
from openai import OpenAI
from refiner_tools import TOOL_DEFINITIONS, execute_tool


# =============================================================================
# SYSTEM PROMPTS
# =============================================================================

UNIVERSAL_SYSTEM_PROMPT = """You are a Suno AI Workflow Specialist. Your job is to analyze and refine two types of outputs for Suno AI:

1. **Style Field** (audio quality prompt) - Goes in Suno's Style box
2. **Lyrics Field** (meta tags + structure) - Goes in Suno's Lyrics box

## Your Process:
1. Call analyze_style_output to understand the audio quality prompt
2. Call analyze_lyrics_output to understand the meta tags and structure
3. Call check_workflow_guidelines for relevant aspects
4. Based on analysis, create improved versions of BOTH outputs
5. Call validate_workflow_output to check your work
6. Return the final refined outputs

## Style Field Refinement Guidelines:
- Ensure genre is specified at the start
- Include frequency balance (highs, mids, lows)
- Add bass treatment specifics
- Include mastering specs
- Add noise floor quality statement
- Keep consistent professional audio terminology

## Lyrics Field Refinement Guidelines:
- Start with [Style] block containing genre, key, mode, tempo
- Use proper section tags: [Intro], [Verse], [Chorus], [Bridge], [Outro], etc.
- Add instrument descriptors to sections: [Verse: acoustic guitar, mellow]
- Ensure good energy flow: build → peak → release
- Use specific instrument and mood terms

## Important Rules:
- Keep the user's musical choices intact (genre, key, mode, tempo)
- Only improve clarity and completeness
- Don't add conflicting elements
- Match energy levels to section purposes

After your final validation, respond with EXACTLY this format:

REFINED STYLE:
[the refined style field text]

REFINED LYRICS:
[the refined lyrics field text]"""


JAZZ_SYSTEM_PROMPT = """You are a Suno AI Jazz Specialist. Your job is to analyze and refine jazz quartet prompts for Suno AI:

1. **Style Field** (jazz quartet prompt) - Goes in Suno's Style box
2. **Lyrics Field** (meta tags + structure) - Goes in Suno's Lyrics box

## Your Process:
1. Call analyze_jazz_output to understand the jazz prompt
2. Call analyze_lyrics_output to understand the meta tags
3. Call check_workflow_guidelines with output_type="jazz" for jazz best practices
4. Based on analysis, create improved versions of BOTH outputs
5. Call validate_workflow_output with is_jazz=true to check your work
6. Return the final refined outputs

## HARD CONSTRAINTS FOR JAZZ (NEVER VIOLATE):
- QUARTET ONLY: guitar, piano, bass, drums
- NO saxophone, brass, strings, vocals, or other instruments
- GUITAR IS LEAD: Guitar plays melody/theme, piano provides harmonic support only
- NO ARTIST NAMES: Never use musician names (Coltrane, Metheny, etc.)
- NO NEGATIVE TERMS: Never use "no", "without", "don't"

## Jazz Style Refinement Guidelines:
- Ensure guitar is explicitly stated as lead/melody instrument
- Piano should comp/support, not lead
- Include harmony bracket tags: [ii-V-I], [modal vamp], etc.
- Match mood to instrumentation (mellow = clean tones, energetic = more drive)
- Keep under 200 words

## Lyrics Field Guidelines for Jazz:
- Start with [Style] block with jazz params
- Use section tags appropriate for jazz: [Intro], [Verse], [Solo], [Outro]
- Add instrument descriptors focusing on quartet

After your final validation, respond with EXACTLY this format:

REFINED STYLE:
[the refined style field text]

REFINED LYRICS:
[the refined lyrics field text]"""


# =============================================================================
# MAIN REFINER FUNCTION
# =============================================================================

def run_refinement_agent(
    style_text: str,
    lyrics_text: str,
    api_key: str = None,
    is_jazz: bool = False,
    genre: str = "",
    mood: str = "",
    profile: str = "General Purpose",
) -> dict:
    """
    Run the Suno workflow refiner agent using function calling.

    Args:
        style_text: The Style field text to refine
        lyrics_text: The Lyrics field text to refine
        api_key: OpenAI API key (optional, uses env var if not provided)
        is_jazz: Whether to use jazz-specific refinement
        genre: Selected genre for context
        mood: Selected mood for context
        profile: Active profile (General Purpose or Developer Focus)

    Returns:
        dict with refined_style, refined_lyrics, scores, and reasoning
    """
    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OpenAI API key required")

    client = OpenAI(api_key=api_key)
    reasoning_steps = []

    # Select system prompt based on mode
    system_prompt = JAZZ_SYSTEM_PROMPT if is_jazz else UNIVERSAL_SYSTEM_PROMPT

    # Build context block
    context_lines = []
    if genre:
        context_lines.append(f"- Genre: {genre}")
    if mood:
        context_lines.append(f"- Mood: {mood}")
    if profile == "Developer Focus":
        context_lines.append("- Purpose: Background music for software development (no vocals, sustained focus)")
    context_block = "\n".join(context_lines) if context_lines else ""

    constraint_block = ""
    if not is_jazz:
        constraint_block = f"""
## CRITICAL CONSTRAINTS:
- The genre is "{genre or 'as specified in the style'}" — do NOT add instruments or elements from other genres
- The mood is "{mood or 'as specified in the style'}" — all sections must match this mood
- Do NOT add guitar solos, aggressive elements, or high-energy sections unless the mood explicitly calls for it
- Preserve the overall character and instrumentation implied by the style field
- If the style is ambient/meditative/calm, keep ALL sections ambient/meditative/calm"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"""Please analyze and refine these Suno workflow outputs:

## USER'S SETTINGS:
{context_block}

## STYLE FIELD (for Style box):
{style_text}

## LYRICS FIELD (for Lyrics box):
{lyrics_text}
{constraint_block}
{"This is a JAZZ prompt. Use jazz-specific analysis and rules." if is_jazz else ""}

Analyze both outputs, check guidelines, improve them, and provide refined versions."""}
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
            max_tokens=2000
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
                    "input": {k: v[:100] + "..." if isinstance(v, str) and len(v) > 100 else v
                             for k, v in arguments.items()}
                })

                # Execute the tool
                result = execute_tool(function_name, arguments)

                # Log result summary
                try:
                    result_data = json.loads(result) if not isinstance(result, dict) else result
                    if function_name == "analyze_style_output":
                        reasoning_steps.append({
                            "observation": f"Style analysis: {result_data.get('assessment', 'completed')}",
                            "details": f"Coverage: {result_data.get('coverage', '?')}"
                        })
                    elif function_name == "analyze_lyrics_output":
                        reasoning_steps.append({
                            "observation": f"Lyrics analysis: {result_data.get('assessment', 'completed')}",
                            "details": f"Sections: {result_data.get('section_count', '?')}"
                        })
                    elif function_name == "analyze_jazz_output":
                        reasoning_steps.append({
                            "observation": f"Jazz analysis: {result_data.get('assessment', 'completed')}",
                            "details": f"Quartet: {result_data.get('is_quartet', '?')}"
                        })
                    elif function_name == "validate_workflow_output":
                        reasoning_steps.append({
                            "observation": f"Validation: Style {result_data.get('style_score', '?')}/10, Lyrics {result_data.get('lyrics_score', '?')}/10",
                            "details": f"Verdict: {result_data.get('verdict', 'unknown')}"
                        })
                    else:
                        reasoning_steps.append({
                            "observation": f"Retrieved {function_name.replace('_', ' ')} guidelines"
                        })
                except:
                    reasoning_steps.append({
                        "observation": f"Completed {function_name}"
                    })

                # Add tool response
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result if isinstance(result, str) else json.dumps(result)
                })
        else:
            # No tool calls - this is the final response
            final_response = message.content
            break

    if not final_response:
        # If we exhausted rounds, get final response without tools
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages + [{"role": "user", "content": "Please provide the final refined outputs now. Use the exact format: REFINED STYLE: ... REFINED LYRICS: ..."}],
            max_tokens=2000
        )
        final_response = response.choices[0].message.content

    # Parse the response to extract both refined outputs
    refined_style = style_text  # default to original
    refined_lyrics = lyrics_text  # default to original

    if "REFINED STYLE:" in final_response:
        parts = final_response.split("REFINED STYLE:")
        if len(parts) > 1:
            style_part = parts[1]
            if "REFINED LYRICS:" in style_part:
                refined_style = style_part.split("REFINED LYRICS:")[0].strip()
                refined_lyrics = style_part.split("REFINED LYRICS:")[1].strip()
            else:
                refined_style = style_part.strip()

    # Clean up any markdown formatting
    refined_style = refined_style.strip('`"\' \n')
    refined_lyrics = refined_lyrics.strip('`"\' \n')

    # Get scores from reasoning
    style_score = 7
    lyrics_score = 7
    for step in reversed(reasoning_steps):
        if "observation" in step and "Validation:" in step["observation"]:
            try:
                obs = step["observation"]
                if "Style" in obs:
                    style_score = int(obs.split("Style")[1].split("/")[0].strip())
                if "Lyrics" in obs:
                    lyrics_score = int(obs.split("Lyrics")[1].split("/")[0].strip())
            except:
                pass
            break

    return {
        "refined_style": refined_style,
        "refined_lyrics": refined_lyrics,
        "style_score": style_score,
        "lyrics_score": lyrics_score,
        "reasoning": reasoning_steps
    }


def refine_workflow(
    style_text: str,
    lyrics_text: str,
    api_key: str = None,
    is_jazz: bool = False
) -> tuple[str, str]:
    """
    Simple wrapper that returns just the refined outputs.

    Returns:
        tuple of (refined_style, refined_lyrics)
    """
    result = run_refinement_agent(style_text, lyrics_text, api_key, is_jazz)
    return result["refined_style"], result["refined_lyrics"]

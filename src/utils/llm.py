"""Helper functions for LLM"""

import json
from typing import TypeVar, Type, Optional, Any
from pydantic import BaseModel
from utils.progress import progress
import traceback

T = TypeVar('T', bound=BaseModel)

def call_llm(
    prompt: Any,
    model_name: str,
    model_provider: str,
    pydantic_model: Type[T],
    agent_name: Optional[str] = None,
    max_retries: int = 3,
    default_factory = None
) -> T:
    """
    Makes an LLM call with retry logic, handling both Deepseek and non-Deepseek models.

    Args:
        prompt: The prompt to send to the LLM
        model_name: Name of the model to use
        model_provider: Provider of the model
        pydantic_model: The Pydantic model class to structure the output
        agent_name: Optional name of the agent for progress updates
        max_retries: Maximum number of retries (default: 3)
        default_factory: Optional factory function to create default response on failure

    Returns:
        An instance of the specified Pydantic model
    """
    from llm.models import get_model, get_model_info

    model_info = get_model_info(model_name)
    llm = get_model(model_name, model_provider)

    # For non-Deepseek models, we can use structured output
    if not (model_info and model_info.is_deepseek()):
        llm = llm.with_structured_output(
            pydantic_model,
            method="json_mode",
        )

    # Call the LLM with retries
    last_error = None
    for attempt in range(max_retries):
        try:
            # Call the LLM
            result = llm.invoke(prompt)

            # For Deepseek, we need to extract and parse the JSON manually
            if model_info and model_info.is_deepseek():
                parsed_result = extract_json_from_deepseek_response(result.content)
                if parsed_result:
                    return pydantic_model(**parsed_result)
            else:
                return result

        except Exception as e:
            last_error = e
            if agent_name:
                progress.update_status(agent_name, None, f"Error - retry {attempt + 1}/{max_retries}")

            if attempt == max_retries - 1:
                error_msg = (
                    f"Error in LLM call after {max_retries} attempts:\n"
                    f"Model: {model_name} ({model_provider})\n"
                    f"Error: {str(e)}"
                )
                # For debugging, print the error and traceback in the console
                print(error_msg + "\n" + traceback.format_exc())
                if default_factory:
                    try:
                        # Try to create with error info
                        if hasattr(default_factory, '__code__') and 'error_info' in default_factory.__code__.co_varnames:
                            return default_factory(error_info=error_msg)
                        # Fall back to old behavior
                        return default_factory()
                    except:
                        # If all else fails, create a basic error response
                        return create_default_response(pydantic_model, error_msg)
                raise

    # Should never reach here, but just in case
    error_msg = f"Max retries exceeded. Last error: {str(last_error)}"
    return create_default_response(pydantic_model, error_msg)

def create_default_response(model_class: Type[T], error_info: Optional[str] = None) -> T:
    """Creates a safe default response with optional error information."""
    default_values = {}
    for field_name, field in model_class.model_fields.items():
        if field_name == "error_details" and error_info:
            default_values[field_name] = error_info
        elif field.annotation == str:
            default_values[field_name] = "Error in analysis, using default"
        elif field.annotation == float:
            default_values[field_name] = 0.0
        elif field.annotation == int:
            default_values[field_name] = 0
        elif hasattr(field.annotation, "__origin__") and field.annotation.__origin__ == dict:
            default_values[field_name] = {}
        else:
            # For other types (like Literal), try to use the first allowed value
            if hasattr(field.annotation, "__args__"):
                default_values[field_name] = field.annotation.__args__[0]
            else:
                default_values[field_name] = None

    return model_class(**default_values)

def extract_json_from_deepseek_response(content: str) -> Optional[dict]:
    """Extracts JSON from Deepseek's markdown-formatted response."""
    try:
        json_start = content.find("```json")
        if json_start != -1:
            json_text = content[json_start + 7:]  # Skip past ```json
            json_end = json_text.find("```")
            if json_end != -1:
                json_text = json_text[:json_end].strip()
                return json.loads(json_text)
    except Exception as e:
        print(f"Error extracting JSON from Deepseek response: {e}")
    return None

import json
from groq import Groq, RateLimitError   # ✅ added RateLimitError
from Tools import TOOLS
from difflib import SequenceMatcher

class GroqAgent:
    def __init__(self, api_key: str, model: str = "meta-llama/llama-guard-4-12b"):
        self.client = Groq(api_key=api_key)
        self.model = model
        self.last_tool_result = None
        self.last_tool_topic = None  # Topic of the last tool call

    @staticmethod
    def clean_json(text: str) -> str:
        text = text.strip()
        if text.startswith("```"):
            text = text.replace("```json", "").replace("```", "")
        return text.strip()

    @staticmethod
    def is_related(prev_topic: str, current_input: str, threshold: float = 0.4) -> bool:
        """
        Determines if the new user input is related to the previous tool topic.
        Uses a simple similarity measure.
        """
        if not prev_topic:
            return False
        similarity = SequenceMatcher(None, prev_topic.lower(), current_input.lower()).ratio()
        return similarity > threshold

    def decide_tool(self, user_input: str) -> dict:
        tools_description = "\n".join(
            [f"- {name}: {data['description']}, params: {data['params']}" for name, data in TOOLS.items()]
        )
        prompt = f"""
    You are an AI assistant that can call tools. Available tools:
    {tools_description}

    User request: {user_input}

    Guidelines:
    - If the user wants to remember something, store a fact, or retrieve a stored fact, use 'memory_tool'.
    - For memory_tool, use JSON with 'action', 'key', 'value' fields appropriately.
    - Respond ONLY with JSON in this format:
    {{"tool": "<tool_name>", "args": {{...}}}}
    - If no tool is needed, respond with: {{"tool": "none"}}
    """
        try:   # ✅ added try/except
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI agent that selects the correct tool."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )
            response_text = response.choices[0].message.content
            cleaned = self.clean_json(response_text)
            return json.loads(cleaned)
        except RateLimitError as e:   # ✅ handle rate limit
            print(f"Rate limit reached: {e}")
            return {"tool": "none", "error": "Rate limit exceeded. Please try again later."}
        except json.JSONDecodeError:
            return {"tool": "none"}

    def generate_final_answer(self, user_input: str, tool_result: str, history: list) -> str:
        prompt = f"Tool returned: {tool_result}\nRespond in a helpful and conversational way."

        try:   # ✅ added try/except
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a friendly and curious assistant."},
                    *history,  # pass full conversation history
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except RateLimitError as e:   # ✅ handle rate limit
            print(f"Rate limit reached: {e}")
            return "⚠️ Server is busy (rate limit exceeded). Please try again in a few minutes."

    def handle_request(self, user_input: str, history: list = None) -> str:
        if history is None:
            history = []

        # Add current user message to history
        history.append({"role": "user", "content": user_input})

        # Decide tool as before
        tool_decision = self.decide_tool(user_input)
        tool_name = tool_decision.get("tool")
        args = tool_decision.get("args", {})

        tool_result = ""
        if tool_name in TOOLS and tool_name != "none":
            try:
                func = TOOLS[tool_name]["func"]
                tool_result = str(func(**args))
            except Exception as e:
                tool_result = f"Error executing tool: {str(e)}"

        # Add tool result as assistant message
        history.append({"role": "assistant", "content": tool_result})

        # Generate final answer using full history
        final_answer = self.generate_final_answer(user_input, tool_result, history)
        history.append({"role": "assistant", "content": final_answer})

        return final_answer, history


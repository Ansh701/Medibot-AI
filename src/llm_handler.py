import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import logging

logger = logging.getLogger(__name__)


def get_llm_cascade():
    """
    Returns a list of LLM instances in the desired fallback order.
    Checks for API keys and only includes available models.
    """
    llm_providers = []

    # 1. Gemini (Primary)
    if os.environ.get("GOOGLE_API_KEY"):
        try:
            # Using 'convert_system_message_to_human' for compatibility
            llm_providers.append(
                ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",
                    temperature=0.3,
                    convert_system_message_to_human=True
                )
            )
            logger.info("Gemini initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize Gemini: {e}")

    # 2. OpenAI (Fallback 1)
    if os.environ.get("OPENAI_API_KEY"):
        try:
            llm_providers.append(
                ChatOpenAI(
                    model="gpt-4o-mini",
                    temperature=0.3,
                    streaming=True
                )
            )
            logger.info("OpenAI initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize OpenAI: {e}")

    # 3. Anthropic (Fallback 2)
    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            llm_providers.append(
                ChatAnthropic(
                    model='claude-3-5-sonnet-20241022',
                    temperature=0.3
                )
            )
            logger.info("Anthropic initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize Anthropic: {e}")

    if not llm_providers:
        logger.error("No LLM providers could be initialized. Please check your API keys in the .env file.")

        # Create a fallback dummy LLM for testing
        class DummyLLM:
            def invoke(self, prompt):
                class DummyResponse:
                    content = "I'm a medical assistant, but I need proper API keys to function. Please configure your .env file with valid API keys for Google (Gemini), OpenAI, or Anthropic."

                return DummyResponse()

            def stream(self, prompt):
                response = self.invoke(prompt)
                yield type('obj', (object,), {'content': response.content})

        llm_providers.append(DummyLLM())
        logger.warning("Using dummy LLM - please configure API keys")

    logger.info(f"Initialized {len(llm_providers)} LLM provider(s)")
    return llm_providers

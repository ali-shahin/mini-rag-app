class ProviderFactory:

    @staticmethod
    def create(llm_type: str):
        if llm_type == 'openai':
            from .OpenAIProvider import OpenAIProvider
            return OpenAIProvider()
        elif llm_type == 'cohere':
            from .CoHereProvider import CoHereProvider
            return CoHereProvider()
        else:
            raise Exception("Invalid LLM type")

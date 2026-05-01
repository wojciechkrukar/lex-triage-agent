from pydantic_settings import BaseSettings, SettingsConfigDict


class TriageConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""
    deepseek_api_key: str = ""
    together_api_key: str = ""
    groq_api_key: str = ""
    higgsfield_api_key: str = ""

    langsmith_api_key: str = ""
    langsmith_project: str = "lex-triage-agent"
    langsmith_tracing: bool = True

    llm_tier: str = "tier3"
    enable_higgsfield: bool = False

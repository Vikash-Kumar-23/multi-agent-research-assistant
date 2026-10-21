class ConfigurationError(RuntimeError):
    """Raised when required application configuration is unavailable."""


class ResearchError(RuntimeError):
    """Raised for recoverable research workflow errors."""

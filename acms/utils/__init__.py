"""ACMS utility functions."""

from acms.utils.ids import (
    generate_embedding_id,
    generate_episode_id,
    generate_fact_id,
    generate_id,
    generate_session_id,
    generate_turn_id,
    timestamp_id,
)
from acms.utils.markers import (
    calculate_marker_boost,
    detect_markers,
    get_marker_type,
    is_custom_marker,
    merge_markers,
)
from acms.utils.retry import RetryConfig, calculate_delay, retry_with_fallback, with_retry
from acms.utils.tokens import (
    HeuristicTokenCounter,
    TiktokenCounter,
    TokenCounter,
    get_default_token_counter,
)
from acms.utils.validation import (
    validate_content,
    validate_markers,
    validate_metadata,
    validate_relevance_threshold,
    validate_role,
    validate_session_id,
    validate_token_budget,
)
from acms.utils.vectors import cosine_similarity

__all__ = [
    # IDs
    "generate_id",
    "generate_turn_id",
    "generate_episode_id",
    "generate_fact_id",
    "generate_session_id",
    "generate_embedding_id",
    "timestamp_id",
    # Tokens
    "TokenCounter",
    "HeuristicTokenCounter",
    "TiktokenCounter",
    "get_default_token_counter",
    # Retry
    "RetryConfig",
    "with_retry",
    "retry_with_fallback",
    "calculate_delay",
    # Validation
    "validate_role",
    "validate_content",
    "validate_markers",
    "validate_token_budget",
    "validate_session_id",
    "validate_metadata",
    "validate_relevance_threshold",
    # Markers
    "detect_markers",
    "merge_markers",
    "calculate_marker_boost",
    "is_custom_marker",
    "get_marker_type",
    # Vectors
    "cosine_similarity",
]

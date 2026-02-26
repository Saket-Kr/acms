"""Unit tests for vector utilities."""

from __future__ import annotations

from gleanr.utils.vectors import cosine_similarity


class TestCosineSimilarity:
    """Tests for cosine_similarity."""

    def test_identical_vectors(self) -> None:
        assert cosine_similarity([1.0, 0.0, 0.0], [1.0, 0.0, 0.0]) == 1.0

    def test_orthogonal_vectors(self) -> None:
        assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == 0.0

    def test_opposite_vectors(self) -> None:
        result = cosine_similarity([1.0, 0.0], [-1.0, 0.0])
        assert abs(result - (-1.0)) < 1e-9

    def test_zero_vector_returns_zero(self) -> None:
        assert cosine_similarity([0.0, 0.0], [1.0, 1.0]) == 0.0

    def test_mismatched_dimensions_returns_zero(self) -> None:
        assert cosine_similarity([1.0, 2.0], [1.0, 2.0, 3.0]) == 0.0

    def test_similar_vectors(self) -> None:
        result = cosine_similarity([1.0, 0.0, 0.0], [0.9, 0.1, 0.0])
        assert result > 0.9

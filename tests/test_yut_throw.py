"""
Tests for yut stick throwing mechanics.
"""

import pytest
from yoot import YutThrow


class TestYutThrow:
    """Test yut stick throwing."""

    def test_throw_returns_valid_result(self):
        """Test throw returns valid throw name and move value."""
        throw_name, move_value = YutThrow.throw()
        assert throw_name in ['do', 'back_do', 'gae', 'geol', 'yut', 'mo']
        assert 1 <= abs(move_value) <= 5

    def test_throw_move_values(self):
        """Test move values for each throw type."""
        assert YutThrow.get_move_value('do') == 1
        assert YutThrow.get_move_value('back_do') == -1
        assert YutThrow.get_move_value('gae') == 2
        assert YutThrow.get_move_value('geol') == 3
        assert YutThrow.get_move_value('yut') == 4
        assert YutThrow.get_move_value('mo') == 5

    def test_extra_turn_throws(self):
        """Test which throws grant extra turns."""
        assert YutThrow.grants_extra_turn('yut')
        assert YutThrow.grants_extra_turn('mo')
        assert not YutThrow.grants_extra_turn('do')
        assert not YutThrow.grants_extra_turn('back_do')
        assert not YutThrow.grants_extra_turn('gae')
        assert not YutThrow.grants_extra_turn('geol')

    def test_flat_probability(self):
        """Test yut sticks have correct probability setting."""
        assert YutThrow.FLAT_PROBABILITY == 0.6

    def test_throw_probability_distribution(self):
        """Test throw probability distribution over many throws."""
        counts = {'mo': 0, 'do': 0, 'back_do': 0, 'gae': 0, 'geol': 0, 'yut': 0}
        num_throws = 10000

        for _ in range(num_throws):
            throw_name, _ = YutThrow.throw()
            counts[throw_name] += 1

        # Expected probabilities with p=0.6 (allowing 20% variance)
        expected = {
            'mo': 0.0256,      # ~2.6%
            'do': 0.1152,      # ~11.5% (75% of Do throws)
            'back_do': 0.0384, # ~3.8% (25% of Do throws)
            'gae': 0.3456,     # ~34.6%
            'geol': 0.3456,    # ~34.6%
            'yut': 0.1296      # ~13.0%
        }

        for throw_name, expected_prob in expected.items():
            actual_prob = counts[throw_name] / num_throws
            # Allow 20% variance from expected
            assert abs(actual_prob - expected_prob) < expected_prob * 0.2, \
                f"{throw_name}: expected {expected_prob:.4f}, got {actual_prob:.4f}"

    def test_back_do_is_subset_of_do(self):
        """Test that back_do occurs approximately 25% as often as regular do."""
        counts = {'do': 0, 'back_do': 0}
        num_throws = 5000

        for _ in range(num_throws):
            throw_name, _ = YutThrow.throw()
            if throw_name in counts:
                counts[throw_name] += 1

        total_do = counts['do'] + counts['back_do']
        if total_do > 0:
            back_do_ratio = counts['back_do'] / total_do
            # Should be around 0.25 (25%), allow variance
            assert 0.15 < back_do_ratio < 0.35, \
                f"Back Do ratio: {back_do_ratio:.2f} (expected ~0.25)"

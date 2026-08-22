from .models.highrise_models import TipType, TIP_VALUES

class Utils:
    """Stateless helper functions used across the SDK."""

    @staticmethod
    def split_tip(amount: int) -> list[TipType]:
        """Decomposes an amount into the largest valid tip tiers, greedily."""
        if amount <= 0:
            return []

        tiers = sorted(TIP_VALUES.items(), reverse=True)
        result: list[TipType] = []

        for value, tier in tiers:
            while amount >= value:
                result.append(tier)
                amount -= value

        return result
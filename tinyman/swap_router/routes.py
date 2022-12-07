from dataclasses import dataclass

from tinyman.assets import Asset, AssetAmount
from tinyman.v2.exceptions import InsufficientReserve
from tinyman.v2.pools import Pool


@dataclass
class Route:
    asset_in: Asset
    asset_out: Asset
    pools: list[Pool]       # TODO: Naming? pools or path

    def __str__(self):
        return "Route: " + "-> ".join(f"{pool.asset_1.unit_name}/{pool.asset_2.unit_name}" for pool in self.pools)

    # Fixed-Input
    def get_fixed_input_quotes(self, amount_in: int, slippage: float = 0.05):
        quotes = []
        assert self.pools

        current_asset_in_amount = AssetAmount(
            asset=self.asset_in,
            amount=amount_in
        )

        for pool in self.pools:
            quote = pool.fetch_fixed_input_swap_quote(
                amount_in=current_asset_in_amount,
                slippage=slippage,
                refresh=False,
            )

            quotes.append(quote)
            current_asset_in_amount = quote.amount_out

        last_quote = quotes[-1]
        assert last_quote.amount_out.asset.id == self.asset_out.id
        return quotes

    def get_fixed_input_last_quote(self, amount_in: int, slippage: float = 0.05):
        try:
            quotes = self.get_fixed_input_quotes(amount_in=amount_in, slippage=slippage)
        except InsufficientReserve:
            return None

        last_quote = quotes[-1]
        return last_quote

    # Fixed-Output
    def get_fixed_output_quotes(self, amount_out: int, slippage: float = 0.05):
        quotes = []
        assert self.pools

        current_asset_out_amount = AssetAmount(
            asset=self.asset_out,
            amount=amount_out
        )

        for pool in self.pools[::-1]:
            quote = pool.fetch_fixed_output_swap_quote(
                amount_out=current_asset_out_amount,
                slippage=slippage,
                refresh=False,
            )

            quotes.append(quote)
            current_asset_out_amount = quote.amount_in

        quotes.reverse()
        first_quote = quotes[0]
        assert first_quote.amount_in.asset.id == self.asset_in.id
        return quotes

    def get_fixed_output_first_quote(self, amount_out: int, slippage: float = 0.05):
        try:
            quotes = self.get_fixed_output_quotes(amount_out=amount_out, slippage=slippage)
        except InsufficientReserve:
            return None

        first_quote = quotes[0]
        return first_quote

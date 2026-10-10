"""Read-only Bitget spot market adapter for the dashboard's crypto assets."""
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone

API_URL = "https://api.bitget.com/api/v2/spot/market/tickers"


def sync_assets(assets) -> tuple[int, str]:
    """Refresh supported crypto prices from Bitget; keep event context unchanged."""
    query = urllib.parse.urlencode({"productType": "SPOT"})
    request = urllib.request.Request(f"{API_URL}?{query}", headers={"accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            payload = json.load(response)
    except Exception:
        return 0, datetime.now(timezone.utc).isoformat()

    tickers = {row.get("symbol"): row for row in payload.get("data", [])}
    updated = 0
    for asset in assets:
        if asset.asset_type != "crypto":
            continue
        row = tickers.get(f"{asset.symbol}USDT")
        if not row:
            continue
        try:
            price = float(row["lastPr"])
            change = float(row.get("changeUtc24h", row.get("change24h", asset.change_24h))) * 100
            volume = float(row.get("usdtVolume") or row.get("quoteVolume") or asset.volume)
        except (TypeError, ValueError):
            continue
        asset.price = price
        asset.change_24h = round(change, 4)
        asset.volume = round(volume, 2)
        asset.status = "Bitget live"
        asset.sparkline = [price] * len(asset.sparkline)
        updated += 1
    return updated, datetime.now(timezone.utc).isoformat()

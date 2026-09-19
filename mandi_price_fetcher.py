import os
import requests

API_KEY = os.environ.get("DATA_GOV_API_KEY")
RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"
BASE_URL = f"https://api.data.gov.in/resource/{RESOURCE_ID}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

if not API_KEY:
    raise EnvironmentError('DATA_GOV_API_KEY not set. Run: $env:DATA_GOV_API_KEY="your_key_here"')


def fetch_mandi_prices(commodity, state=None, district=None, market=None, limit=10):
    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": limit,
        "filters[commodity]": commodity,
    }
    if state:
        params["filters[state]"] = state
    if district:
        params["filters[district]"] = district
    if market:
        params["filters[market]"] = market

    try:
        resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERROR] Live fetch failed: {e}")
        return None

    data = resp.json()
    records = data.get("records", [])

    if not records:
        print(f"[WARN] No records found for commodity={commodity}, state={state}, district={district}, market={market}.")
        return None

    results = []
    for r in records:
        results.append({
            "state": r.get("state"),
            "district": r.get("district"),
            "market": r.get("market"),
            "commodity": r.get("commodity"),
            "variety": r.get("variety"),
            "grade": r.get("grade"),
            "arrival_date": r.get("arrival_date"),
            "min_price": r.get("min_price"),
            "max_price": r.get("max_price"),
            "modal_price": r.get("modal_price"),
        })
    return results


def print_price_trend(commodity, state=None, district=None, market=None):
    data = fetch_mandi_prices(commodity, state, district, market)

    if not data:
        print(f"Falling back to static data for {commodity} (live source unavailable or no matching records).\n")
        return

    print(f"\nLive Mandi Price Trend - {commodity}")
    print("-" * 70)
    for row in data:
        print(f"{row['arrival_date']} | {row['market']} ({row['district']}, {row['state']}) [{row['variety']}]: Min Rs {row['min_price']} / Max Rs {row['max_price']} / Modal Rs {row['modal_price']} per quintal")
    print()


if __name__ == "__main__":
    print_price_trend("Potato", state="Gujarat", district="Ahmedabad")
    print_price_trend("Rice", state="Gujarat")
    print_price_trend("Tomato", state="Gujarat", district="Ahmedabad")

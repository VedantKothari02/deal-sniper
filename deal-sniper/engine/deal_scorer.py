def score_deal(product_data: dict) -> int:
    """
    Scores a deal based on heuristics.

    Rules:
    discount > 70% → +40 points
    discount > 50% → +25 points
    price drop (mrp - price) > 1000 INR → +20 points

    keywords in name (ssd, router, gpu, headphones) → +20 points
    """
    score = 0
    discount = product_data.get('discount', 0)
    price = product_data.get('price', 0)
    mrp = product_data.get('mrp', 0)
    name = product_data.get('product_name', '').lower()

    # Check discount
    if discount > 70:
        score += 40
    elif discount > 50:
        score += 25

    # Check absolute price drop
    price_drop = mrp - price
    if price_drop > 1000:
        score += 20

    # Check keywords
    keywords = ['ssd', 'router', 'gpu', 'headphones']
    if any(kw in name for kw in keywords):
        score += 20

    return score

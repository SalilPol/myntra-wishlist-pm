"""
Blocker taxonomy for wishlist non-conversion on Myntra.

Every classified document is tagged against these categories. The same
taxonomy drives the LLM classifier, the heuristic fallback, the opportunity
scoring, and the dashboard, so a change here propagates everywhere.

Addressability and latency weights are analyst assumptions and are shown
in the dashboard as assumptions, not findings.
"""

BLOCKERS = {
    "FIT_SIZE": {
        "label": "Fit and size uncertainty",
        "desc": "Unsure which size to pick, brand sizing inconsistent, past fit failures.",
        "addressable_without_money": 0.9,
        "latency_impact": 0.9,
        "keywords": ["size", "sizing", "fit", "fits", "fitting", "tight", "loose",
                     "small", "large", "xl", "measurement", "size chart", "runs"],
    },
    "LOOK_STYLE": {
        "label": "Will it look right on me",
        "desc": "Colour accuracy, how it looks on a real body, what to pair it with.",
        "addressable_without_money": 0.8,
        "latency_impact": 0.8,
        "keywords": ["colour", "color", "looks different", "look on me", "suit me",
                     "styling", "style it", "pair", "outfit", "picture", "photo",
                     "in real", "actual product"],
    },
    "QUALITY": {
        "label": "Fabric and quality doubt",
        "desc": "Fabric feel, durability, 'looks cheap', quality vs price.",
        "addressable_without_money": 0.7,
        "latency_impact": 0.7,
        "keywords": ["quality", "fabric", "material", "cheap looking", "looks cheap", "flimsy",
                     "stitching", "too thin", "very thin", "durable", "shrink", "fade"],
    },
    "PRICE_WAIT": {
        "label": "Waiting for a sale or better price",
        "desc": "Deferring for EORS, coupons, price drops; price vs perceived value.",
        "addressable_without_money": 0.2,
        "latency_impact": 0.9,
        "keywords": ["sale", "eors", "discount", "coupon", "price drop", "expensive",
                     "cheaper", "offer", "deal", "wait for", "waiting for"],
    },
    "OCCASION_TIMING": {
        "label": "Saved for a future occasion",
        "desc": "Wedding, trip, season, festival; no urgency yet.",
        "addressable_without_money": 0.6,
        "latency_impact": 0.6,
        "keywords": ["wedding", "trip", "vacation", "diwali", "festival", "occasion",
                     "next month", "winter", "summer", "later", "someday", "eventually"],
    },
    "AVAILABILITY": {
        "label": "Size or item sold out before deciding",
        "desc": "Wishlist decays: size gone, item delisted, restock unknown.",
        "addressable_without_money": 0.8,
        "latency_impact": 0.9,
        "keywords": ["out of stock", "sold out", "size not available", "unavailable",
                     "removed", "restock", "not available", "gone", "delisted"],
    },
    "RETURN_HASSLE": {
        "label": "Fear of return or exchange",
        "desc": "Return policy confusion, refund delay, pickup failures, non-returnable.",
        "addressable_without_money": 0.6,
        "latency_impact": 0.7,
        "keywords": ["return", "refund", "exchange", "pickup", "non returnable",
                     "not returnable", "return policy", "try and buy", "try & buy"],
    },
    "DELIVERY_TRUST": {
        "label": "Delivery and seller trust",
        "desc": "Delivery delays, wrong or damaged item, seller reliability.",
        "addressable_without_money": 0.5,
        "latency_impact": 0.5,
        "keywords": ["delivery", "delivered", "late", "damaged", "wrong item", "fake",
                     "seller", "courier", "packaging", "duplicate"],
    },
    "SOCIAL_VALIDATION": {
        "label": "Needs a second opinion",
        "desc": "Asks friends or partner, shares screenshots, seeks approval before buying.",
        "addressable_without_money": 0.8,
        "latency_impact": 0.8,
        "keywords": ["friend", "sister", "wife", "husband", "girlfriend", "boyfriend",
                     "opinion", "screenshot", "ask", "show", "whatsapp", "mom", "mother"],
    },
    "ALTERNATIVES": {
        "label": "Comparing with other options",
        "desc": "Cross-platform or cross-brand comparison, decision paralysis.",
        "addressable_without_money": 0.6,
        "latency_impact": 0.7,
        "keywords": ["compare", "comparison", "ajio", "amazon", "flipkart", "nykaa",
                     "meesho", "zara", "h&m", "alternative", "similar", "options",
                     "shortlist", "confused between"],
    },
    "BOOKMARK_ONLY": {
        "label": "Wishlist used as inspiration board",
        "desc": "Saving with no purchase intent; wishlist as a mood board.",
        "addressable_without_money": 0.3,
        "latency_impact": 0.2,
        "keywords": ["inspiration", "mood board", "just saving", "just save", "bookmark",
                     "for later", "no intention", "not buying", "collection", "browse"],
    },
    "APP_UX": {
        "label": "Wishlist tooling is weak",
        "desc": "No sorting, notes, folders, comparison, or reminders in the wishlist.",
        "addressable_without_money": 0.9,
        "latency_impact": 0.6,
        "keywords": ["no folders", "sorting", "no sort", "filter wishlist", "folder", "add notes",
                     "reminder", "remind me", "organise", "organize", "clutter", "too many items",
                     "compare them", "side by side", "cannot find anything"],
    },
}

INTENT_TYPES = ["buy_soon", "sale_wait", "occasion", "inspiration", "unsure", "unknown"]

SEGMENT_FIELDS = {
    "gender": ["female", "male", "unknown"],
    "age_band": ["18-24", "25-34", "35-44", "45+", "unknown"],
    "city_tier": ["metro", "tier2_3", "unknown"],
    "category": ["western_wear", "ethnic_wear", "footwear", "accessories",
                 "beauty", "kids", "unknown"],
    "price_band": ["under_800", "800_2500", "over_2500", "unknown"],
    "tenure": ["new", "repeat", "unknown"],
}

CATEGORY_ORDER = list(BLOCKERS.keys())

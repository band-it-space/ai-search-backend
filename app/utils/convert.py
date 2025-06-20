def parse_float(value) -> float:
    try:
        return float(str(value).replace(",", "."))
    except Exception:
        return 0.0

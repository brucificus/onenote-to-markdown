def parse_html_style_attribute(style: str) -> dict:
    style_dict = {}
    for style_pair in style.split(";"):
        if style_pair.strip() == "":
            continue
        style_pair = style_pair.strip()
        style_key, style_value = style_pair.split(":")
        style_dict[style_key.strip()] = style_value.strip()
    return style_dict


def build_html_style_attribute(style_dict: dict) -> str:
    style_pairs = []
    for style_key, style_value in style_dict.items():
        style_pairs.append(f"{style_key}:{style_value}")
    return "; ".join(style_pairs)

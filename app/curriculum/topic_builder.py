def generate_new_topics(month: int, theme: str):

    base_templates = [
        f"Fun learning story about {theme} for kids",
        f"Adventure story about {theme}",
        f"Interactive learning game about {theme}",
    ]

    return [
        {
            "month": month,
            "category": "Educational",
            "title": title
        }
        for title in base_templates
    ]

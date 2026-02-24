from app.curriculum.base_topics import all_topics


def get_topics_by_month(month: int):
    return [t for t in all_topics if t["month"] == month]


def get_all_topics():
    return all_topics

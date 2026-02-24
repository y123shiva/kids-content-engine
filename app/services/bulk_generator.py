from app.curriculum.curriculum_manager import get_topics_by_month
from app.services.script_generator import generate_script
from app.dataset.dataset_saver import save_script


def generate_month_dataset(month: int, version="v1"):

    topics = get_topics_by_month(month)
    results = []

    for idx, topic in enumerate(topics, start=1):

        topic_id = f"m{month}_{idx:03d}"

        # ✅ Pass full topic dictionary
        script = generate_script(topic)

        data = {
            "topic_id": topic_id,
            "month": month,
            "category": topic["category"],
            "title": topic["title"],
            "script": script
        }

        file_path = save_script(data, month, version)

        results.append(file_path)

    return results

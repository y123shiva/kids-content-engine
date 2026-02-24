import json
import random
import os
from pathlib import Path

# # --- Configuration ---
# BASE_OUTPUT_DIR = "data/Bibo_and_Friends_Lab"
# os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)

# Example topics (keep your full all_topics list here)
all_topics = [
    # Month 1
    {"month":1,"category":"Educational","title":"POP! POP! Learn Our Bouncy Balloon Colors!"},
    {"month":1,"category":"Educational","title":"Shape Stomp! Can You Find the Circle?"},
    {"month":1,"category":"Educational","title":"Fuzzy, Smooth, SQUISHY Colors!"},
    {"month":1,"category":"Educational","title":"Shape Builders! What Can We MAKE?"},
    {"month":1,"category":"Educational","title":"Yummy Colors! Taste the Rainbow!"},
    {"month":1,"category":"Moral Story","title":"The Kind Elephant and the Lost Bird"},
    {"month":1,"category":"Moral Story","title":"Happy, Sad, SILLY! What's Your Face Do?"},
    {"month":1,"category":"Moral Story","title":"I Can Help! Tiny Helper SUPER Power!"},
    {"month":1,"category":"Moral Story","title":"Oops! Let's Say Sorry with a Hug!"},
    {"month":1,"category":"Moral Story","title":"Sharing Your Voice: When to Say 'Wait!'"},
    {"month":1,"category":"Fun Activity","title":"DIY Color Sorting Game at Home"},
    {"month":1,"category":"Fun Activity","title":"Sticker Power! Dot-to-Dot Fun!"},
    # Month 2
    {"month":2,"category":"Educational","title":"Count the Ducks! Wiggle Your Fingers!"},
    {"month":2,"category":"Educational","title":"The Big vs. Small Parade!"},
    {"month":2,"category":"Educational","title":"Fast & Slow: Animal Race!"},
    {"month":2,"category":"Educational","title":"JUMP and Count to 10! Jungle Friend Fun!"},
    {"month":2,"category":"Educational","title":"BLAST OFF! Count By Twos to the Moon!"},
    {"month":2,"category":"Moral Story","title":"The Honest Fox and the Missing Treat (Truth)"},
    {"month":2,"category":"Moral Story","title":"Why Telling the Truth Makes You a Hero"},
    {"month":2,"category":"Moral Story","title":"The Lost Coin and the Brave Child"},
    {"month":2,"category":"Moral Story","title":"I Can Share! Little Helpers Story"},
    {"month":2,"category":"Moral Story","title":"Oops! Fixing Mistakes Together"},
    {"month":2,"category":"Fun Activity","title":"Number Hopscotch"},
    {"month":2,"category":"Fun Activity","title":"Make a DIY Counting Bead Necklace"},
    # Month 3
    {"month":3,"category":"Educational","title":"DANCE the Letters! The Ultimate ABC Song!"},
    {"month":3,"category":"Educational","title":"A-B-C Sound Sensation! Can You Say AH?"},
    {"month":3,"category":"Educational","title":"Find the Letter Challenge!"},
    {"month":3,"category":"Educational","title":"Match the Giant Letter to the Tiny Letter!"},
    {"month":3,"category":"Educational","title":"Alphabet Builders! Stack & Spell Fun!"},
    {"month":3,"category":"Moral Story","title":"Listen and Learn! Why We Respect Others!"},
    {"month":3,"category":"Moral Story","title":"Helping Hands: The Story of Two Friends"},
    {"month":3,"category":"Moral Story","title":"Please and Thank You – Magic Words Story"},
    {"month":3,"category":"Moral Story","title":"The Respectful Kitten & Big Adventure"},
    {"month":3,"category":"Moral Story","title":"Friendship Circle: Sharing is Fun!"},
    {"month":3,"category":"Fun Activity","title":"Alphabet Matching Cards DIY"},
    {"month":3,"category":"Fun Activity","title":"Paint Your ABC Wall Poster"},
    # Month 4
    {"month":4,"category":"Educational","title":"Moo, Oink, Baa! Farm Animal Sound Challenge!"},
    {"month":4,"category":"Educational","title":"Under the Sea: Ocean Animals"},
    {"month":4,"category":"Educational","title":"Grow Tall Like a Tree! Nature Movement Game!"},
    {"month":4,"category":"Educational","title":"Stomp the Puddles! The Weather Dance Game!"},
    {"month":4,"category":"Educational","title":"Cloud Watching Magic: What Shape is the Cloud!"},
    {"month":4,"category":"Moral Story","title":"The Ants and the Teamwork Tree"},
    {"month":4,"category":"Moral Story","title":"How the Birds Built a Nest Together"},
    {"month":4,"category":"Moral Story","title":"The Lost Puppy and the Helpful Kids"},
    {"month":4,"category":"Moral Story","title":"I Can Help! Nature Friends Story"},
    {"month":4,"category":"Moral Story","title":"Sharing is Caring: Forest Adventure"},
    {"month":4,"category":"Fun Activity","title":"Nature Scavenger Hunt"},
    {"month":4,"category":"Fun Activity","title":"Leaf Printing Art"},
    # Month 5
    {"month":5,"category":"Educational","title":"Why the Sky is Blue? For Kids"},
    {"month":5,"category":"Educational","title":"Splash! Does it SINK or FLOAT? Water Fun!"},
    {"month":5,"category":"Educational","title":"Day and Night Explained"},
    {"month":5,"category":"Educational","title":"Magic Stick! Does It Stick or Slip Game!"},
    {"month":5,"category":"Educational","title":"Floating vs Sinking Objects"},
    {"month":5,"category":"Moral Story","title":"Say 'Thank You!' The Happy Heart Tree Story"},
    {"month":5,"category":"Moral Story","title":"The Little Star Who Shared Its Light"},
    {"month":5,"category":"Moral Story","title":"Gratitude Makes Us Happy"},
    {"month":5,"category":"Moral Story","title":"Sharing is Fun! Family Story"},
    {"month":5,"category":"Moral Story","title":"Helping Hands: Magic Gratitude Tale"},
    {"month":5,"category":"Fun Activity","title":"DIY Rain Cloud in a Jar"},
    {"month":5,"category":"Fun Activity","title":"Make a Simple Compass"},
    # Month 6
    {"month":6,"category":"Educational","title":"Happy Day! Let's Dance to World Festivals!"},
    {"month":6,"category":"Educational","title":"Point to the Colors! The Flag Matching Game!"},
    {"month":6,"category":"Educational","title":"Traditional Clothes from Different Countries"},
    {"month":6,"category":"Educational","title":"Build a Tower! Amazing Buildings Around the World!"},
    {"month":6,"category":"Educational","title":"Famous Landmarks for Kids"},
    {"month":6,"category":"Moral Story","title":"Brave Roar! The Story of Finding Your Courage!"},
    {"month":6,"category":"Moral Story","title":"Standing Up for What is Right"},
    {"month":6,"category":"Moral Story","title":"The Lion Cub’s First Roar of Courage"},
    {"month":6,"category":"Moral Story","title":"I Can Be Brave! Tiny Heroes Story"},
    {"month":6,"category":"Moral Story","title":"Courage Circle: Face Your Fears Together"},
    {"month":6,"category":"Fun Activity","title":"Make Your Own Festival Lantern"},
    {"month":6,"category":"Fun Activity","title":"Family Quiz Night Game"},
    # Month 7
    {"month":7,"category":"Educational","title":"Zoom Zoom! Learn About Cars and Trucks!"},
    {"month":7,"category":"Educational","title":"Choo Choo! All About Trains for Kids"},
    {"month":7,"category":"Educational","title":"Up in the Air! Planes and Helicopters!"},
    {"month":7,"category":"Educational","title":"Safe Streets! Traffic Lights and Signs Fun"},
    {"month":7,"category":"Educational","title":"Fast or Slow? Vehicles Movement Game"},
    {"month":7,"category":"Moral Story","title":"The Little Bus That Could Share Its Ride"},
    {"month":7,"category":"Moral Story","title":"Be Safe! Teddy Learns Rules Story"},
    {"month":7,"category":"Moral Story","title":"Helping Hands: Cleaning Up the Park"},
    {"month":7,"category":"Moral Story","title":"Waiting is Fun! Patience Tale for Kids"},
    {"month":7,"category":"Moral Story","title":"The Honest Driver Story"},
    {"month":7,"category":"Fun Activity","title":"Build a Mini Road with Blocks"},
    {"month":7,"category":"Fun Activity","title":"Create Your Own Traffic Sign Game"},
    # Month 8
    {"month":8,"category":"Educational","title":"Blast Off! Learn About the Solar System"},
    {"month":8,"category":"Educational","title":"Twinkle Twinkle! Stars and Constellations Fun"},
    {"month":8,"category":"Educational","title":"Planets Parade! Name the Planets"},
    {"month":8,"category":"Educational","title":"Moon Adventures! Craters and More"},
    {"month":8,"category":"Educational","title":"Astronaut Training! Jump and Move Game"},
    {"month":8,"category":"Moral Story","title":"Curious Cat Explores the Night Sky"},
    {"month":8,"category":"Moral Story","title":"The Brave Star Finder Story"},
    {"month":8,"category":"Moral Story","title":"Sharing Knowledge: Space Friends Tale"},
    {"month":8,"category":"Moral Story","title":"Persistence Pays! Little Rocket Learns Story"},
    {"month":8,"category":"Moral Story","title":"Teamwork in Space! Story for Kids"},
    {"month":8,"category":"Fun Activity","title":"Build a Paper Rocket Experiment"},
    {"month":8,"category":"Fun Activity","title":"Create Your Own Solar System Mobile"}
]


# # ---------------- INTERACTIVE CUES ----------------
# INTERACTIVE_CUES = ["[CLAP]", "[JUMP]", "[STOMP]", "[SHAKE]", "[SPIN]"]

# # ---------------- TTS VARIATIONS ----------------
# def generate_tts_variations(narration: str, num_variations=3):
#     return [f"{narration} (TTS option {i+1})" for i in range(num_variations)]

# # ---------------- SCRIPT GENERATOR ----------------
# def generate_script(topic: dict):
#     num_scenes = random.randint(3, 6)
#     scenes = []

#     for i in range(1, num_scenes + 1):
#         narration = f"Scene {i}: Let's explore {topic['title']}!"
#         scene = {
#             "scene_number": i,
#             "narration": narration,
#             "visuals": f"Visuals for scene {i} of {topic['title']}",
#             "tts_variations": generate_tts_variations(narration)
#         }

#         if random.random() < 0.7:
#             scene["cues"] = [random.choice(INTERACTIVE_CUES)]

#         scenes.append(scene)

#     # ✅ script created AFTER loop
#     script = {
#         "month": topic["month"],
#         "category": topic["category"],
#         "title": topic["title"],
#         "scenes": scenes
#     }

#     return script

# # ---------------- SAVE SCRIPT ----------------
# def save_script(script: dict):
#     month_dir = Path(BASE_OUTPUT_DIR) / f"Month_{script['month']}" / script["category"]
#     month_dir.mkdir(parents=True, exist_ok=True)

#     safe_title = (
#         script["title"]
#         .replace(" ", "_")
#         .replace("!", "")
#         .replace("?", "")
#         .replace("'", "")
#     )

#     file_path = month_dir / f"{safe_title}.json"

#     with open(file_path, "w", encoding="utf-8") as f:
#         json.dump(script, f, ensure_ascii=False, indent=2)

#     print(f"✅ Saved: {file_path}")

# # ---------------- MAIN ----------------
# for topic in all_topics:
#     script_json = generate_script(topic)
#     save_script(script_json)

# print("\n🎉 All scripts generated successfully!")

import matplotlib.pyplot as plt
import re
import matplotlib.pyplot as plt
import re

def plot_personality_donut_chart(traits: dict, filename: str):
    fig, axes = plt.subplots(1, len(traits), figsize=(len(traits)*3, 4))
    if len(traits) == 1:
        axes = [axes]  # Ensure axes is iterable if there's only one trait

    colors = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336']

    for ax, (trait, value), color in zip(axes, traits.items(), colors):
        # Pie chart (donut style)
        ax.pie([value, 100 - value],
               startangle=90,
               colors=[color, '#E0E0E0'],
               wedgeprops={'width': 0.4, 'edgecolor': 'white'})

        ax.set(aspect="equal")
        ax.set_title(f"{trait}\n{value}%", fontsize=10)

    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def extract_and_plot_traits(response_text):
    pattern = r"Extraversion: (\d+)% Openness: (\d+)% Conscientiousness: (\d+)% Agreeableness: (\d+)% Neuroticism: (\d+)%"
    match = re.search(pattern, response_text)
    if match:
        traits = {
            "Extraversion": int(match.group(1)),
            "Openness": int(match.group(2)),
            "Conscientiousness": int(match.group(3)),
            "Agreeableness": int(match.group(4)),
            "Neuroticism": int(match.group(5))
        }
        chart_file = "personality_donut_chart.png"
        plot_personality_donut_chart(traits, chart_file)


extract_and_plot_traits("""You're a mindful and calm individual, even in challenging times!

That's amazing! It takes a lot of self-awareness and emotional intelligence to stay grounded.

Well, that's all the questions I have for now! Based on our conversation, here are some personality insights:

Big Five Personality Traits:

Extraversion: 75% Openness: 85% Conscientiousness: 60% Agreeableness: 40% Neuroticism: 20%

Song Suggestion: You might love the song "Best Day of My Life" by American Authors - it's upbeat, adventurous, and optimistic!

Gift Idea: A thoughtful gift for you might be a personalized travel journal or a set of adventure-themed notecards. It would encourage your sense of exploration and self-reflection.

Wow, you're an amazing person! Keep being your awesome self!""")
import ollama
import re
import matplotlib.pyplot as plt
conversation = [{'role': 'system', 'content': '"evaluate the conversation using below format :\nExtraversion : 0-100%\nOpenness : 0-100%\nConscientiousness : 0-100%\nAgreeableness : 0-100%\nNeuroticism : 0-100%\n\nalso add a suggested song they might love, based on their personality.\nAn ideal gift idea for them.\n\nthis is the conversation : "'}, 
{'role': 'user', 'content': 'hi Sandy my name is John'}, 
{'role': 'assistant', 'content': "Nice to meet you, John! So, I'm curious... what's the thing that usually gets you out of bed in the morning? Is it a good cup of coffee, a project you're working on, or something else entirely?"}, 
{'role': 'user', 'content': "tell me about the things that I'm going to do today is actually the best thing I"}, 
{'role': 'assistant', 'content': "John! So, you're looking forward to doing something special today. That's great! What's one thing you've been putting off or wanting to tackle for a while now, and are you planning on getting it done today?"}, 
{'role': 'user', 'content': "so because I'm currently focusing on my work"}, {'role': 'assistant', 'content': "John! So, your work is keeping you busy and focused right now. That's really great that you're prioritizing it! What is it about your job or current project that gets you excited and motivated to tackle new challenges?"}, {'role': 'user', 'content': 'building a product that'}, 
{'role': 'assistant', 'content': "Exciting stuff, John! You're building a product, huh? What kind of product are we talking about here? Is it something entirely new, an iteration of something existing, or even a solution to a problem you've encountered yourself?"}, 
{'role': 'user', 'content': "I'm providing a product that helps users to assess about their own personality"}, 
{'role': 'assistant', 'content': 'Fascinating! So, your product is helping people gain insights into their personalities. That\'s really cool! What do you think is the most valuable takeaway or "aha" moment that people get from using your product? Is it helping them understand themselves better, making new connections, or something else entirely?'}, 
{'role': 'user', 'content': "what's to help them understand themselves better"}, 
{'role': 'assistant', 'content': "So, helping people understand themselves better is a big part of what you're aiming for. That's really important! Have you found that there are certain personality traits or characteristics that tend to be surprisingly common among your users, or perhaps some that they might not have realized about themselves before using your product?"}, 
{'role': 'user', 'content': "having some kinds of natural products that can be interacted by user is the most important thing so I'm helping people"}, {'role': 'assistant', 'content': "I love that approach, John! So, you're creating a platform where users can engage with natural products in a way that's meaningful to them. That's really wonderful! How do you think your product helps people connect with their personalities and emotions on a deeper level? For example, are there specific features or exercises that help users tap into their intuition, creativity, or emotional intelligence?"},
{'role': 'assistant', 'content': "So, it's about helping people sink deeper into understanding their own personality. That's really profound! What do you think is the biggest misconception that people have about themselves, and how does your product help them overcome that?"}, {'role': 'user', 'content': 'dropping them to understand about'}, 
{'role': 'user', 'content': 'sink understanding their personality is the'},  
{'role': 'assistant', 'content': "John, I love where this is going! So, it's about dropping people into a deeper understanding of their own personality. That's really beautiful! What do you think is the most empowering or life-changing aspect of self-discovery for your users? Is there something that you've seen make a significant impact on their lives, whether it's relationships, career choices, or simply feeling more confident and true to themselves?"}]
def preprocess(conversation: list):
    # Process the conversation as described
    result = []
    # Keep the first element as is
    result.append(conversation[0])

    # Combine user and assistant content
    combined_content = ""
    for i in range(1, len(conversation), 2):
        combined_content += f"user: {conversation[i]['content']}\n "
        if i + 1 < len(conversation):
            combined_content += f"assistant: {conversation[i+1]['content']}\n "

    # Append the combined content
    result.append({'role': 'user', 'content': combined_content.strip()})
    return result
# print(preprocess(conversation))
final_eval = ollama.chat(
            model='llama3',
            messages= preprocess(conversation)
        )

final_summary = re.sub(r'(\([^)]*\)|\*)', '', final_eval['message']['content']).strip()
print(final_summary)

def plot_personality_donut_chart(traits: dict, filename: str):
    fig, axes = plt.subplots(1, len(traits), figsize=(len(traits)*3, 4))
    if len(traits) == 1:
        axes = [axes]  # Ensure axes is iterable if there's only one trait

    colors = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336']

    for ax, (trait, value), color in zip(axes, traits.items(), colors):
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
    pattern = r"Extraversion\s*:\s*(\d+)%\s*Openness\s*:\s*(\d+)%\s*Conscientiousness\s*:\s*(\d+)%\s*Agreeableness\s*:\s*(\d+)%\s*Neuroticism\s*:\s*(\d+)%"
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

extract_and_plot_traits(final_summary)
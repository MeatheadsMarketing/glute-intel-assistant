# assistants/plan_generator.py (PRL+ upgraded with intelligence selector)

import openai
import os

# OpenAI API key should be stored in environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

# Top 20 trusted sources for glute transformation (used in GPT conditioning)
INTELLIGENCE_PROFILES = [
    "Bret Contreras (The Glute Guy)",
    "Dr. Brad Schoenfeld (Hypertrophy Expert)",
    "Jeff Nippard (Science-Based Training)",
    "NASM (National Academy of Sports Medicine)",
    "NSCA (National Strength and Conditioning Association)",
    "Precision Nutrition Coaches",
    "Stronger by Science",
    "Biomechanics Institute (Kelly Starrett / Jill Miller)",
    "Mass Research Review (Menno Henselmans, Greg Nuckols)",
    "Girls Gone Strong (Women’s Strength Org)",
    "OPEX Fitness", 
    "Athlean-X (Jeff Cavaliere)",
    "N1 Training (Kassem Hanson)",
    "Physique Development Coaches",
    "TrainHeroic Coaches’ Network",
    "Glute Lab (San Diego)",
    "Dr. Layne Norton (Biolayne)",
    "Myolean Fitness (Research-based coaching)",
    "Stronger U Fitness",
    "Body by Bret Academy"
]

def generate_glute_plan(glute_tags: list, user_fitness_level="Intermediate", goals="Aesthetic Shape + Strength", expert_source="Bret Contreras") -> str:
    """
    Generates a glute plan conditioned on the expert source selected.
    """
    prompt = f"""
You are acting as a personal coach trained under the glute transformation philosophy of: {expert_source}.
Create a weekly glute-building workout plan tailored to someone with the following traits:
- Glute Tags: {', '.join(glute_tags)}
- Fitness Level: {user_fitness_level}
- Goal: {goals}

Include:
- Weekly workout structure (e.g. 3-day split)
- Specific glute and hip exercises
- Progression strategy over time
- Focus areas based on tags (e.g. shelf, dips, symmetry)
- Recommendations for training volume, rest, and rep ranges
Respond in clear markdown format as if you were delivering this to a client.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a top-tier personal trainer and program designer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=900
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error generating plan: {str(e)}"


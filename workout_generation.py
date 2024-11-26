import os
from openai import OpenAI
import subprocess
import sys

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
import json
import re
import logging

# Set up logging to file
logging.basicConfig(filename='output.log', level=logging.DEBUG, format='%(asctime)s %(message)s')

# Set up OpenAI API key from environment variable

def extract_json_from_response(response_text):
    # Use regular expression to extract JSON content
    match = re.search(r'\{.*\}', response_text, re.DOTALL)
    if match:
        return match.group(0)
    else:
        raise ValueError("No JSON content found in the response")

def generate_input_json(prompt, output_file):
    logging.info("Starting generate_input_json with prompt: %s", prompt)
    # Call the OpenAI API with the provided prompt
    response = client.chat.completions.create(model="gpt-4",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=1500,
    temperature=0.7)

    # Debugging: Log the raw response
    logging.debug("Raw response: %s", response)

    # Extract the generated text
    generated_text = response.choices[0].message.content.strip()

    # Debugging: Log the generated text
    logging.debug("Generated text: %s", generated_text)

    # Extract JSON content from the generated text
    try:
        json_content = extract_json_from_response(generated_text)
        input_json = json.loads(json_content)
    except (json.JSONDecodeError, ValueError) as e:
        logging.error("Error decoding JSON: %s", e)
        return

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Write the JSON to the output file
    with open(output_file, "w") as file:
        json.dump(input_json, file, indent=4)
    logging.info("Generated input JSON saved to %s", output_file)

    # Run circuit_generation.py on the generated file
    subprocess.run(["python", "circuit_generation.py", output_file, "test"])
    logging.info("Ran circuit_generation.py on %s", output_file)

def get_default_prompt():
    return """
    Generate a workout plan in JSON format with the following structure. Only include the JSON content in your response:
    {
        "timers": [
            {
                "identifier": "unique-identifier-1",
                "exercises": [
                    {"name": "Exercise 1", "duration": 30, "color": 3},
                    {"name": "Exercise 2", "duration": 30, "color": 3}
                ],
                "name": "Timer Name 1",
                "color": 3,
                "numberOfSets": 1,
                "soundScheme": 17,
                "overrun": false,
                "notes": "Notes for Timer 1",
                "activity": 0,
                "music": {
                    "resume": true,
                    "volume": 1,
                    "persist": false,
                    "shuffle": false,
                    "query": {}
                },
                "warmup": {
                    "name": "Warm Up",
                    "duration": 0,
                    "split": false,
                    "indefinite": false,
                    "ducked": false,
                    "rest": true,
                    "splitRest": 0,
                    "music": {
                        "volume": 1,
                        "resume": false,
                        "query": {},
                        "persist": false,
                        "shuffle": false
                    },
                    "halfwayAlert": false,
                    "color": 3
                }
            },
            {
                "identifier": "unique-identifier-2",
                "exercises": [
                    {"name": "Exercise 3", "duration": 45, "color": 6},
                    {"name": "Exercise 4", "duration": 45, "color": 6},
                    {"name": "Exercise 5", "duration": 45, "color": 6}
                ],
                "name": "Timer Name 2",
                "color": 6,
                "numberOfSets": 2,
                "soundScheme": 18,
                "overrun": true,
                "notes": "Notes for Timer 2",
                "activity": 1,
                "music": {
                    "resume": false,
                    "volume": 0.8,
                    "persist": true,
                    "shuffle": true,
                    "query": {}
                },
                "warmup": {
                    "name": "Warm Up",
                    "duration": 5,
                    "split": true,
                    "indefinite": true,
                    "ducked": true,
                    "rest": false,
                    "splitRest": 10,
                    "music": {
                        "volume": 0.5,
                        "resume": true,
                        "query": {},
                        "persist": true,
                        "shuffle": true
                    },
                    "halfwayAlert": true,
                    "color": 4
                }
            },
            {
                "identifier": "unique-identifier-3",
                "exercises": [
                    {"name": "Exercise 6", "duration": 30, "color": 5},
                    {"name": "Exercise 7", "duration": 30, "color": 5}
                ],
                "name": "Timer Name 3",
                "color": 5,
                "numberOfSets": 1,
                "soundScheme": 19,
                "overrun": false,
                "notes": "Notes for Timer 3",
                "activity": 2,
                "music": {
                    "resume": true,
                    "volume": 1,
                    "persist": false,
                    "shuffle": false,
                    "query": {}
                },
                "warmup": {
                    "name": "Warm Up",
                    "duration": 0,
                    "split": false,
                    "indefinite": false,
                    "ducked": false,
                    "rest": true,
                    "splitRest": 0,
                    "music": {
                        "volume": 1,
                        "resume": false,
                        "query": {},
                        "persist": false,
                        "shuffle": false
                    },
                    "halfwayAlert": false,
                    "color": 3
                }
            }
        ]
    }
    """

def load_prompt_from_file(prompt_file):
    with open(prompt_file, 'r') as file:
        return file.read().strip()

def compare_json_structure(json1, json2, path=""):
    if type(json1) != type(json2):
        print(f"Type mismatch at {path}: {type(json1)} != {type(json2)}")
        return False
    if isinstance(json1, dict):
        keys1 = set(json1.keys())
        keys2 = set(json2.keys())
        if keys1 != keys2:
            print(f"Key mismatch at {path}: {keys1} != {keys2}")
            return False
        for key in sorted(keys1):
            if not compare_json_structure(json1[key], json2[key], path + f".{key}"):
                return False
    elif isinstance(json1, list):
        if len(json1) != len(json2):
            print(f"List length mismatch at {path}: {len(json1)} != {len(json2)}")
            print(f"Output list at {path}: {json1}")
            print(f"Example list at {path}: {json2}")
            return False
        for index, (item1, item2) in enumerate(zip(json1, json2)):
            if not compare_json_structure(item1, item2, path + f"[{index}]"):
                return False
    return True

def test_output_structure(output_file, example_file):
    if not os.path.exists(example_file):
        print(f"Example file not found: {example_file}")
        return

    with open(output_file, 'r') as file:
        output_json = json.load(file)

    with open(example_file, 'r') as file:
        example_json = json.load(file)

    if compare_json_structure(output_json, example_json):
        print("The structures match.")
    else:
        print("The structures do not match.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python workout_generation.py <output_file> [prompt_file]")
        sys.exit(1)

    output_file = sys.argv[1]
    
    if len(sys.argv) > 2:
        prompt_file = sys.argv[2]
        prompt = load_prompt_from_file(prompt_file)
    else:
        prompt = get_default_prompt()

    # Save the generated JSON to /inputs/FILENAME.json
    output_file = os.path.join("inputs", os.path.basename(output_file).replace(".txt", ".json"))
    generate_input_json(prompt, output_file)
    # Test the output structure
    example_file = "workout_structures/example_workout.json"
    test_output_structure(output_file, example_file)

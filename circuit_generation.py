import json
import os
from collections import OrderedDict

def create_circuit_timer(identifier, name, color, cooldown, numberOfSets, type, intervals, warmup, setRest, notes, random, music, group, overrun, soundScheme, activity, intervalRest):
    circuit_timer = OrderedDict([
        ("group", group),
        ("numberOfSets", numberOfSets),
        ("intervals", intervals),
        ("activity", activity),
        ("identifier", identifier),
        ("overrun", overrun),
        ("cooldown", cooldown),
        ("setRest", setRest),
        ("music", music),
        ("notes", notes),
        ("warmup", warmup),
        ("type", type),
        ("soundScheme", soundScheme),
        ("name", name),
        ("intervalRest", intervalRest),
        ("random", random),
        ("color", color)
    ])
    return circuit_timer

def generate_exercise(name, duration, split=False, color=6, halfwayAlert=False, ducked=False, splitRest=0, indefinite=False, rest=False, music=None):
    if music is None:
        music = {"resume": False, "persist": False, "query": {}, "shuffle": False, "volume": 1}
    
    exercise = {
        "name": name,
        "duration": duration,
        "split": split,
        "color": color,
        "halfwayAlert": halfwayAlert,
        "ducked": ducked,
        "splitRest": splitRest,
        "indefinite": indefinite,
        "rest": rest,
        "music": music
    }
    return exercise

def create_folder(name, identifier, items, color=None):
    folder = OrderedDict([
        ("name", name),
        ("identifier", identifier),
        ("items", items)
    ])
    if color is not None:
        folder["color"] = color
    return folder

def compare_json_structure(json1, json2, path=""):
    if type(json1) != type(json2):
        print(f"Type mismatch at {path}: {type(json1)} != {type(json2)}")
        return False
    if isinstance(json1, dict):
        if set(json1.keys()) != set(json2.keys()):
            print(f"Key mismatch at {path}: {set(json1.keys())} != {set(json2.keys())}")
            return False
        for key in json1:
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
    # Read the input.json file
    with open('input.json', 'r') as file:
        config = json.load(file)

    timers = []

    for timer_config in config['timers']:
        identifier = timer_config['identifier']
        exercise_duration = timer_config['exercise_duration']
        name = timer_config['name']
        color = timer_config['color']
        numberOfSets = timer_config['numberOfSets']
        soundScheme = timer_config['soundScheme']
        overrun = timer_config['overrun']
        notes = timer_config['notes']
        activity = timer_config['activity']
        music = timer_config['music']
        warmup = timer_config['warmup']

        # Generate exercises
        exercises = [generate_exercise(f"Exercise {i+1}", exercise_duration, color=color) for i in range(timer_config['num_warmups'] + timer_config['num_main'] + timer_config['num_cooldowns'])]

        # Create circuit timer
        circuit_timer = create_circuit_timer(
            identifier=identifier,
            name=name,
            color=color,
            cooldown=None,
            numberOfSets=numberOfSets,
            type=3,
            intervals=exercises,
            warmup=None,
            setRest=None,
            notes=notes,
            random=True,
            music=music,
            group=True,
            overrun=overrun,
            soundScheme=soundScheme,
            activity=activity,
            intervalRest=None
        )

        timers.append(circuit_timer)

    # Create folder to wrap the circuit timers
    inner_folder = create_folder("imports", "A6168CEE-475B-4DFD-8861-54E69AC67F0A", timers, color=3)
    outer_folder = create_folder("Exported Items", "972BEE15-AEAE-4FD8-9783-C80A79A36F94", [inner_folder])

    # Convert to JSON and write to file
    folder_json = json.dumps(outer_folder, indent=4)
    output_file = "timer_folder.seconds"
    with open(output_file, "w") as file:
        file.write(folder_json)

    # Test the output structure
    example_file = os.path.join("example-exports", "2 circuit timers in folder.seconds")
    test_output_structure(output_file, example_file)
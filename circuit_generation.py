import json
import os
import sys
from collections import OrderedDict
from datetime import datetime

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

def compare_json_content(json1, json2, path=""):
    if type(json1) != type(json2):
        print(f"Type mismatch at {path}: {type(json1)} != {type(json2)}")
        return False
    if isinstance(json1, dict):
        if set(json1.keys()) != set(json2.keys()):
            print(f"Key mismatch at {path}: {set(json1.keys())} != {set(json2.keys())}")
            return False
        for key in json1:
            if not compare_json_content(json1[key], json2[key], path + f".{key}"):
                return False
    elif isinstance(json1, list):
        if len(json1) != len(json2):
            print(f"List length mismatch at {path}: {len(json1)} != {len(json2)}")
            return False
        for index, (item1, item2) in enumerate(zip(json1, json2)):
            if not compare_json_content(item1, item2, path + f"[{index}]"):
                return False
    else:
        if json1 != json2:
            print(f"Value mismatch at {path}: {json1} != {json2}")
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

def test_output_content(output_file, example_file):
    if not os.path.exists(example_file):
        print(f"Example file not found: {example_file}")
        return

    with open(output_file, 'r') as file:
        output_json = json.load(file)

    with open(example_file, 'r') as file:
        example_json = json.load(file)

    if compare_json_content(output_json, example_json):
        print("The content matches.")
    else:
        print("The content does not match.")

def main(input_file):
    # Read the input JSON file from the specified path
    with open(input_file, 'r') as file:
        config = json.load(file)

    timers = []

    for timer_config in config['timers']:
        identifier = timer_config['identifier']
        name = timer_config['name']
        color = timer_config['color']
        numberOfSets = timer_config['numberOfSets']
        soundScheme = timer_config['soundScheme']
        overrun = timer_config['overrun']
        notes = timer_config['notes']
        activity = timer_config['activity']
        music = timer_config['music']
        warmup = timer_config['warmup']
        intervals = timer_config['intervals']  # Use 'intervals' instead of 'exercises'
        intervalRest = timer_config.get('intervalRest', {
            "indefinite": False,
            "music": {"persist": False, "shuffle": False, "volume": 1, "query": {}, "resume": False},
            "halfwayAlert": False,
            "split": False,
            "ducked": False,
            "splitRest": 0,
            "rest": True,
            "duration": 10,
            "name": "Rest",
            "color": 1
        })
        setRest = timer_config.get('setRest', {
            "ducked": False,
            "duration": 15,  # Change duration to 15
            "split": False,
            "color": 1,
            "splitRest": 0,
            "name": "Rest",
            "halfwayAlert": False,
            "rest": True,
            "music": {"persist": False, "shuffle": False, "query": {}, "volume": 1, "resume": False},
            "indefinite": False
        })
        cooldown = timer_config.get('cooldown', {
            "name": "Cool Down",
            "duration": 0,
            "split": False,
            "indefinite": False,
            "ducked": False,
            "rest": True,
            "splitRest": 0,
            "music": {"volume": 1, "resume": False, "query": {}, "persist": False, "shuffle": False},
            "halfwayAlert": False,
            "color": 5
        })

        # Create circuit timer
        circuit_timer = create_circuit_timer(
            identifier=identifier,
            name=name,
            color=color,
            cooldown=cooldown,  # Ensure cooldown is included
            numberOfSets=numberOfSets,
            type=3,
            intervals=intervals,  # Use 'intervals' instead of 'exercises'
            warmup=warmup,
            setRest=setRest,
            notes=notes,
            random=True,
            music=music,
            group=True,
            overrun=overrun,
            soundScheme=soundScheme,
            activity=activity,
            intervalRest=intervalRest
        )

        timers.append(circuit_timer)

    # Create folder to wrap the circuit timers
    inner_folder = create_folder("imports", "A6168CEE-475B-4DFD-8861-54E69AC67F0A", timers, color=3)
    outer_folder = create_folder("Exported Items", "972BEE15-AEAE-4FD8-9783-C80A79A36F94", [inner_folder])

    # Convert to JSON and write to file
    timestamp = datetime.now().strftime("%m-%d-%H-%M")
    output_file = f"output/{os.path.splitext(os.path.basename(input_file))[0]}_{timestamp}.seconds"
    folder_json = json.dumps(outer_folder, indent=4)  # Use outer_folder directly
    with open(output_file, "w") as file:
        file.write(folder_json)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python circuit_generation.py <input_file> [test]")
        sys.exit(1)

    input_file = sys.argv[1]
    main(input_file)

    if len(sys.argv) > 2 and sys.argv[2] == "test":
        # Test the output structure
        example_file = "workout_structures/example_workout.json"
        timestamp = datetime.now().strftime("%m-%d-%H-%M")
        output_file = f"output/{os.path.splitext(os.path.basename(input_file))[0]}_{timestamp}.seconds"
        test_output_structure(output_file, example_file)
        test_output_content(output_file, example_file)
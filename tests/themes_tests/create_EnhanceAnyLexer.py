import json


def main() -> None:
    palette_path = "../../configs/themes/palettes.json"
    
    with open(palette_path, "r") as f:
        data = json.load(f)
    
    result = extract_key_values(data)
    
    with open("EnhanceAnyLexer_Output.txt", "w") as f:
        for k, v in result:
            f.write(f"{k} = {v}\n")


def extract_key_values(d, result=None):
    if result is None:
        result = []

    for key, value in d.items():
        if isinstance(value, dict):
            extract_key_values(value, result)
        else:
            result.append((f'0x{value[5:7]}{value[3:5]}{value[1:3]}', f'"{value}"'))
    
    return result


if __name__ == "__main__":
    main()

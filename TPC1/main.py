from typing import Dict, Final, List, Tuple

DATASET_PATH: Final[str] = "emd.csv"
DATASET_SEPARATOR: Final[str] = ","

MODALITY_INDEX: Final[int] = 8 # 9th column
RESULT_INDEX: Final[int] = 12 # 13th column
AGE_INDEX: Final[int] = 5 # 6th column

AGE_GROUP_INTERVAL: Final[int] = 5

def read_dataset(path: str) -> List[str]:
    """Reads the dataset from the given path and returns a list of lines."""
    try:
        with open(path, "r") as file:
            file.readline() # Skip header
            return file.readlines()
    except FileNotFoundError:
        print(f"Error: file '{path}' not found")
        exit(1)
    
def dedup_list(lst: List[str]) -> List[str]:
    """Returns a list with the unique elements of the given list."""
    return list(set(lst))

def main() -> None:
    modalities: List[str] = []
    results: List[bool] = []
    age_group_distribution: Dict[Tuple[int, int], int] = {}

    content: List[str] = read_dataset(DATASET_PATH)
    for line in content:
        line = line.strip().split(DATASET_SEPARATOR)
        modalities.append(line[MODALITY_INDEX])
        results.append(line[RESULT_INDEX].lower() == "true")

        age: int = int(line[AGE_INDEX])
        age_group: Tuple[int, int] = (age - age % AGE_GROUP_INTERVAL, age - age % AGE_GROUP_INTERVAL + AGE_GROUP_INTERVAL - 1)
        age_group_distribution[age_group] = age_group_distribution.get(age_group, 0) + 1

    modalities = sorted(dedup_list(modalities))

    print("Lista ordenadada alfabeticamente das modalidades:")
    print(modalities)
    print()

    passed: int = len([r for r in results if r])
    passed_percentage: float = passed / len(results) * 100
    total: int = len(results)

    print(f"Percentagem de atletas aptos: {passed_percentage:.2f}% ({passed}/{total})")
    print(f"Percentagem de atletas inaptos: {100 - passed_percentage:.2f}% ({total - passed}/{total})")
    print()

    print(f"Distribuição de atletas por escalão etário em intervalos de {AGE_GROUP_INTERVAL} anos:")
    for age_group in sorted(age_group_distribution.keys()):
        print(f"{age_group[0]}-{age_group[1]}: {age_group_distribution[age_group]}")

if __name__ == "__main__":
    main()

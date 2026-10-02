from pathlib import Path

DERIVED_DIRECTORY_NAMES = {"processed", "train", "validation", "test"}


def count_source_files(dataset_dir: Path) -> int:
    if not dataset_dir.is_dir():
        return 0

    return sum(
        1
        for path in dataset_dir.rglob("*")
        if path.is_file()
        and not any(part.startswith(".") for part in path.relative_to(dataset_dir).parts)
        and path.relative_to(dataset_dir).parts[0] not in DERIVED_DIRECTORY_NAMES
    )
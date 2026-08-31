from pathlib import Path

from devpilot.models.repository import (
    RepositoryFileContent,
)


DEFAULT_MAX_CHARACTERS = 20_000


def read_repository_file(
    repository_path: str,
    relative_file_path: str,
    max_characters: int = DEFAULT_MAX_CHARACTERS,
) -> RepositoryFileContent:
    root = Path(repository_path).resolve()

    if not root.exists():
        raise FileNotFoundError(
            f"Repository path does not exist: {root}"
        )

    if not root.is_dir():
        raise NotADirectoryError(
            f"Repository path is not a directory: {root}"
        )

    file_path = (
        root / relative_file_path
    ).resolve()

    if root not in file_path.parents:
        raise ValueError(
            "Requested file is outside the repository."
        )

    if not file_path.exists():
        raise FileNotFoundError(
            f"File does not exist: {relative_file_path}"
        )

    if not file_path.is_file():
        raise ValueError(
            f"Path is not a file: {relative_file_path}"
        )

    content = file_path.read_text(
        encoding="utf-8"
    )

    truncated = (
        len(content) > max_characters
    )

    if truncated:
        content = content[:max_characters]

    return RepositoryFileContent(
        path=relative_file_path,
        content=content,
        truncated=truncated,
    )
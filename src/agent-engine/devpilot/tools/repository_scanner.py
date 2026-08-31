from pathlib import Path

from devpilot.models.repository import (
    RepositoryFile,
    RepositorySummary,
)

from devpilot.tools.repository_config import (
    IGNORED_DIRECTORIES,
)

def scan_repository(
    repository_path: str,
) -> RepositorySummary:
    root = Path(repository_path).resolve()

    if not root.exists():
        raise FileNotFoundError(
            f"Repository path does not exist: {root}"
        )

    if not root.is_dir():
        raise NotADirectoryError(
            f"Repository path is not a directory: {root}"
        )

    files: list[RepositoryFile] = []

    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue

        relative_path = file_path.relative_to(root)

        if any(
            part in IGNORED_DIRECTORIES
            for part in relative_path.parts
        ):
            continue

        files.append(
            RepositoryFile(
                path=str(relative_path),
                extension=file_path.suffix.lower(),
                size_bytes=file_path.stat().st_size,
            )
        )

    detected_extensions = sorted(
        {
            file.extension
            for file in files
            if file.extension
        }
    )

    return RepositorySummary(
        root_path=str(root),
        total_files=len(files),
        files=files,
        detected_extensions=detected_extensions,
    )
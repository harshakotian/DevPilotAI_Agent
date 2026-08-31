from pathlib import Path

from devpilot.models.repository import (
    CodeSearchMatch,
    CodeSearchResult,
)

from devpilot.tools.repository_config import (
    IGNORED_DIRECTORIES,
    SEARCHABLE_EXTENSIONS,
)

DEFAULT_MAX_MATCHES = 50


def search_code(
    repository_path: str,
    query: str,
    max_matches: int = DEFAULT_MAX_MATCHES,
) -> CodeSearchResult:
    if not query.strip():
        raise ValueError(
            "Search query cannot be empty."
        )

    root = Path(repository_path).resolve()

    if not root.exists():
        raise FileNotFoundError(
            f"Repository path does not exist: {root}"
        )

    matches: list[CodeSearchMatch] = []

    normalized_query = query.lower()

    for file_path in root.rglob("*"):
        if len(matches) >= max_matches:
            break

        if not file_path.is_file():
            continue

        relative_path = file_path.relative_to(root)

        if any(
            part in IGNORED_DIRECTORIES
            for part in relative_path.parts
        ):
            continue

        if (
            file_path.suffix.lower()
            not in SEARCHABLE_EXTENSIONS
        ):
            continue

        try:
            content = file_path.read_text(
                encoding="utf-8"
            )
        except UnicodeDecodeError:
            continue

        for line_number, line in enumerate(
            content.splitlines(),
            start=1,
        ):
            if normalized_query in line.lower():
                matches.append(
                    CodeSearchMatch(
                        path=str(relative_path),
                        line_number=line_number,
                        line=line.strip(),
                    )
                )

                if len(matches) >= max_matches:
                    break

    return CodeSearchResult(
        query=query,
        total_matches=len(matches),
        matches=matches,
    )
from pydantic import BaseModel, Field


class RepositoryFile(BaseModel):
    path: str = Field(
        description="Path relative to the repository root."
    )

    extension: str = Field(
        description="File extension."
    )

    size_bytes: int = Field(
        description="File size in bytes."
    )

class RepositorySummary(BaseModel):
    root_path: str

    total_files: int

    files: list[RepositoryFile] = Field(
        default_factory=list
    )

    detected_extensions: list[str] = Field(
        default_factory=list
    )

class RepositoryFileContent(BaseModel):
    path: str = Field(
        description="Path relative to the repository root."
    )

    content: str = Field(
        description="Text content of the source file."
    )

    truncated: bool = Field(
        default=False,
        description="Whether the returned content was truncated."
    )

class CodeSearchMatch(BaseModel):
    path: str

    line_number: int

    line: str

class CodeSearchResult(BaseModel):
    query: str

    total_matches: int

    matches: list[CodeSearchMatch] = Field(
        default_factory=list
    )

class RepositoryEvidenceItem(BaseModel):
    source: str = Field(
        description="Repository file that supports this evidence."
    )

    line_number: int | None = Field(
        default=None,
        description="Line number when available."
    )

    evidence: str = Field(
        description="Relevant repository evidence."
    )


class RepositoryAnalysis(BaseModel):
    repository_type: str = Field(
        description=(
            "Detected application or repository type, "
            "for example ASP.NET Core Web API."
        )
    )

    architecture_summary: str = Field(
        description=(
            "Concise summary of the architecture visible "
            "from repository evidence."
        )
    )

    relevant_files: list[str] = Field(
        default_factory=list,
        description=(
            "Files likely relevant to the requested change."
        ),
    )

    existing_capabilities: list[str] = Field(
        default_factory=list,
        description=(
            "Capabilities confirmed to already exist "
            "in the repository."
        ),
    )

    missing_capabilities: list[str] = Field(
        default_factory=list,
        description=(
            "Capabilities requested or expected but not "
            "found in the collected evidence."
        ),
    )

    likely_impact_areas: list[str] = Field(
        default_factory=list,
        description=(
            "Areas likely to require modification."
        ),
    )

    evidence: list[RepositoryEvidenceItem] = Field(
        default_factory=list,
        description=(
            "Repository evidence supporting the analysis."
        ),
    )

    uncertainties: list[str] = Field(
        default_factory=list,
        description=(
            "Claims that cannot yet be confirmed from "
            "available evidence."
        ),
    )

    confidence: str = Field(
        description=(
            "Overall confidence: low, medium, or high."
        )
    )

class RepositoryEvidence(BaseModel):
    repository_summary: RepositorySummary

    searches: list[CodeSearchResult] = Field(
        default_factory=list
    )

    files: list[RepositoryFileContent] = Field(
        default_factory=list
    )
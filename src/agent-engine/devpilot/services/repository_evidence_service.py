from devpilot.models.repository import (
    RepositoryEvidence,
)
from devpilot.tools.code_search import (
    search_code,
)
from devpilot.tools.file_reader import (
    read_repository_file,
)
from devpilot.tools.repository_scanner import (
    scan_repository,
)


class RepositoryEvidenceService:
    def collect(
        self,
        repository_path: str,
    ) -> RepositoryEvidence:
        repository_summary = scan_repository(
            repository_path
        )

        product_search = search_code(
            repository_path=repository_path,
            query="Product",
        )

        redis_search = search_code(
            repository_path=repository_path,
            query="Redis",
        )

        cache_search = search_code(
            repository_path=repository_path,
            query="cache",
        )

        files_to_read = [
            "Program.cs",
            "Services/IProductService.cs",
            "Services/ProductService.cs",
            "Controllers/ProductsController.cs",
        ]

        file_contents = []

        available_paths = {
            file.path
            for file in repository_summary.files
        }

        for relative_path in files_to_read:
            if relative_path not in available_paths:
                continue

            content = read_repository_file(
                repository_path=repository_path,
                relative_file_path=relative_path,
            )

            file_contents.append(content)

        return RepositoryEvidence(
            repository_summary=repository_summary,
            searches=[
                product_search,
                redis_search,
                cache_search,
            ],
            files=file_contents,
        )
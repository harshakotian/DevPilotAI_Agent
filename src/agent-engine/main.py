from devpilot.graph.workflow import build_workflow


def main():
    workflow = build_workflow()

    initial_state = {
        "requirement": (
            "Add distributed caching to the Product API "
            "using Redis."
            # "Make the system better."
        ),
        "repository_path": (
            "../../samples/SampleProductApi"
        ),
        "status": "new",
    }

    result = workflow.invoke(
        initial_state
    )

    print()
    print("Workflow complete")
    print("Status:", result["status"])

    analysis = result[
        "requirement_analysis"
    ]

    print()
    print(
        analysis.model_dump_json(
            indent=2
        )
    )

    if "repository_summary" in result:
        repository_summary = result[
            "repository_summary"
        ]

        print()
        print("Repository Summary")
        print(
            repository_summary.model_dump_json(
                indent=2
            )
        )

    if "repository_analysis" in result:
        repository_analysis = result[
            "repository_analysis"
        ]

        print()
        print("Repository Analysis")
        print()

        print(
            repository_analysis.model_dump_json(
                indent=2
            )
        )

    if "architecture_proposal" in result:
        architecture = result[
            "architecture_proposal"
        ]

        print()
        print("Architecture Proposal")
        print()

        print(
            architecture.model_dump_json(
                indent=2
            )
        )

    if "implementation_plan" in result:
        implementation_plan = result[
            "implementation_plan"
        ]

        print()
        print("Implementation Plan")
        print()

        print(
            implementation_plan.model_dump_json(
                indent=2
            )
        )

if __name__ == "__main__":
    main()
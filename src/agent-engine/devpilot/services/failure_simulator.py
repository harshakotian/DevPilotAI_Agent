class FailureSimulator:
    def __init__(self):
        self._repository_timeout_triggered = False

    def reset(self) -> None:
        self._repository_timeout_triggered = False

    def maybe_fail_repository(
        self,
        fail_once: bool,
        fail_always: bool,
    ) -> None:
        if fail_always:
            raise TimeoutError(
                "Simulated persistent repository timeout."
            )

        if (
            fail_once
            and not self._repository_timeout_triggered
        ):
            self._repository_timeout_triggered = True

            raise TimeoutError(
                "Simulated temporary repository timeout."
            )


failure_simulator = FailureSimulator()
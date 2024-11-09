from typing import Any, Optional

from pydantic import BaseModel, Field

BEST_EFFORT = -999999999
MIN_DIRECTIVE = 0
MAX_DIRECTIVE = 100


class Directives(BaseModel):
    session_id: Optional[str] = Field(
        description="The current session ID if this belongs to a session", default=None
    )
    latency: int = Field(
        description=f"How the server should prioritize low latency, from {MIN_DIRECTIVE} to {MAX_DIRECTIVE}. If not specified, the server will infer the best value.",
        default=BEST_EFFORT,
    )
    accuracy: int = Field(
        description=f"How the server should prioritize high accuracy of the results, from {MIN_DIRECTIVE} to {MAX_DIRECTIVE}. If not specified, the server will infer the best value.",
        default=BEST_EFFORT,
    )
    cost: int = Field(
        description=f"How the server should prioritize minimizing costs, from {MIN_DIRECTIVE} to {MAX_DIRECTIVE}. If not specified, the server will infer the best value.",
        default=BEST_EFFORT,
    )
    reproducibility: int = Field(
        description=f"How the server should prioritize returning the same result as previous queries of similar nature, from {MIN_DIRECTIVE} to {MAX_DIRECTIVE}. If not specified, the server will infer the best value.",
        default=BEST_EFFORT,
    )
    freshness: int = Field(
        description=f"How the server should prioritize freshness, from {MIN_DIRECTIVE} to {MAX_DIRECTIVE}. If not specified, the server will infer the best value.",
        default=BEST_EFFORT,
    )
    personalization: int = Field(
        description=f"How the server should prioritize personalization, from {MIN_DIRECTIVE} to {MAX_DIRECTIVE}. If not specified, the server will infer the best value.",
        default=BEST_EFFORT,
    )
    recall: int = Field(
        description=f"How the server should prioritize recall in future queries for the same session, from {MIN_DIRECTIVE} to {MAX_DIRECTIVE}. If not specified, the server will infer the best value.",
        default=BEST_EFFORT,
    )
    creativity: int = Field(
        description=f"How the server should prioritize creativity in the results, from {MIN_DIRECTIVE} to {MAX_DIRECTIVE}. If not specified, the server will infer the best value.",
        default=BEST_EFFORT,
    )

    def __init__(
        self,
        *,
        session_id: Optional[str] = None,
        latency: int = BEST_EFFORT,
        accuracy: int = BEST_EFFORT,
        cost: int = BEST_EFFORT,
        reproducibility: int = BEST_EFFORT,
        freshness: int = BEST_EFFORT,
        personalization: int = BEST_EFFORT,
        recall: int = BEST_EFFORT,
        creativity: int = BEST_EFFORT,
        **data: Any,
    ):
        super().__init__(**data)
        self.session_id = session_id
        self.latency = latency
        self.cost = cost
        self.accuracy = accuracy
        self.reproducibility = reproducibility
        self.personalization = personalization
        self.freshness = freshness
        self.recall = recall
        self.creativity = creativity
        self.validate_directives()

    def override_with(self, directives: Optional["Directives"]) -> "Directives":
        if directives is None:
            return self

        def override_val(value: int, other: int) -> int:
            if value == BEST_EFFORT:
                return other
            if other != BEST_EFFORT:
                return other
            return value

        return Directives(
            session_id=directives.session_id or self.session_id,
            latency=override_val(self.latency, directives.latency),
            accuracy=override_val(self.accuracy, directives.accuracy),
            cost=override_val(self.cost, directives.cost),
            reproducibility=override_val(
                self.reproducibility, directives.reproducibility
            ),
            freshness=override_val(self.freshness, directives.freshness),
            personalization=override_val(
                self.personalization, directives.personalization
            ),
            recall=override_val(self.recall, directives.recall),
            creativity=override_val(self.creativity, directives.creativity),
        )

    def validate_directives(self) -> None:
        """Validates the directive values.

        Directives must be between 0 and 100 or -1 for best effort. No two directives can have the same value, except for -1.

        """
        directive_kv = self.model_dump()

        directive_numbers = [
            int(directive_kv[directive])
            for directive in directive_kv
            if isinstance(directive_kv[directive], int)
        ]
        if len(directive_numbers) != 8:
            raise ValueError(
                f"Expected 8 directive values, found {len(directive_numbers)} in {directive_kv}."
            )

        for n in directive_numbers:
            if n == BEST_EFFORT:
                continue
            if n < MIN_DIRECTIVE or n > MAX_DIRECTIVE:
                raise ValueError(
                    f"Directive value must be between {MIN_DIRECTIVE} and {MAX_DIRECTIVE} or {BEST_EFFORT}. Found {n} in {directive_kv}."
                )

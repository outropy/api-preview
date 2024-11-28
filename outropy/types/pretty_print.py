from typing import Any, List


def to_class_name(instance: Any) -> str:
    return str(instance.__class__.__name__)


def to_class_names(instances: List[Any]) -> List[str]:
    return [to_class_name(instance) for instance in instances]

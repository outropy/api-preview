import unittest
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from outropy.types.pydantic_to_schema import recursive_convert_pydantic_to_dict


class ChildModel(BaseModel):
    urn: str = Field(description="The URN of the child model")
    name: str = Field(description="The name of the child model")
    parent: str = Field(description="The URN of the parent model")
    list: List[Dict[Any, int]] = Field(description="A list of dictionaries", default=[])


class ParentModel(BaseModel):
    urn: str = Field(description="The URN of the parent model")
    name: str = Field(description="The name of the parent model")
    children: List[ChildModel] = Field(
        description="The children of the parent model", default=[]
    )


class TestRecursiveConvertPydanticToDict(unittest.TestCase):
    def test_converts_whole_tree(self) -> None:
        parent = ParentModel(
            urn="urn:parent",
            name="Parent",
            children=[
                ChildModel(
                    urn="urn:child1",
                    name="Child 1",
                    parent="urn:parent",
                    list=[{1: 1}, {2: 2}],
                ),
                ChildModel(
                    urn="urn:child2",
                    name="Child 2",
                    parent="urn:parent",
                    list=[{3: 3}, {4: 4}],
                ),
            ],
        )

        result = recursive_convert_pydantic_to_dict(parent)

        self.assertEqual(
            result,
            {
                "urn": "urn:parent",
                "name": "Parent",
                "children": [
                    {
                        "urn": "urn:child1",
                        "name": "Child 1",
                        "parent": "urn:parent",
                        "list": [{1: 1}, {2: 2}],
                    },
                    {
                        "urn": "urn:child2",
                        "name": "Child 2",
                        "parent": "urn:parent",
                        "list": [{3: 3}, {4: 4}],
                    },
                ],
            },
        )

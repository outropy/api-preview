import hashlib
import re
import urllib
import uuid
from typing import Annotated, Any, List, Optional, Type
from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
    TypeAdapter,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    model_serializer,
)
from pydantic.functional_validators import WrapValidator

from outropy.copypasta.exceptions import IllegalArgumentError
from outropy.copypasta.observability import logging
from outropy.copypasta.typing_ext import SupportsStr

valid_segment = r"^[a-zA-Z0-9._%-]+$"

logger = logging.get_logger(__name__)

_urn_secret = "378eihdnwknsjkxbvc"


def try_uuid(value: str) -> Optional[UUID]:
    try:
        return UUID(value)
    except ValueError:
        return None


def escaped(value: str) -> str:
    return urllib.parse.quote(value)


def unescaped(value: str) -> str:
    return urllib.parse.unquote(value)


# URN needs to import BaseModel and not PydanticBaseModel to avoid circular dependencies
class RawUrn(BaseModel):
    namespace: str = Field("Namespace of the collection, usually outropy")
    collection: str = Field("Collection name, usually the name of the entity or table")
    encoded_identifier: str = Field(
        "URL-escaped ID of an entity, usually the primary-key or a proxy to it"
    )

    def __init__(
        self, secret: str, namespace: str, collection: str, identifier: SupportsStr
    ) -> None:
        if secret != _urn_secret:
            raise IllegalArgumentError(
                "Do not instantiate Urn directly, use a a factory method instead"
            )

        super().__init__(
            namespace=self._validated_segment(namespace),
            collection=self._validated_segment(collection),
            encoded_identifier=self._validated_identifier(identifier),
        )

    def _validated_segment(self, segment: Optional[SupportsStr]) -> str:
        if segment is None:
            raise IllegalArgumentError("URN segment cannot be None")
        segment_str = str(segment)
        if len(segment_str) == 0:
            raise IllegalArgumentError("URN segment cannot be empty")
        if segment_str == "None":
            # TODO: this requires fixing a million unrelated tests
            logger.warning(
                "URN segment is the string 'None'. This is probably a mistake. If it's not, please ignore this warning."
            )
            return segment_str

        if not re.match(valid_segment, segment_str):
            raise IllegalArgumentError(
                f"URN segment [{segment}] is not valid. It must match the regex: {valid_segment}"
            )
        return segment_str

    @classmethod
    def _validated_identifier(cls, segment: Optional[SupportsStr]) -> str:
        # TODO: this requires fixing a million unrelated tests
        segment_str = str(segment)
        if len(segment_str.lstrip().rstrip()) == 0:
            raise IllegalArgumentError("URN identifier cannot be empty")
        if segment_str == "None":
            logger.warning(
                "URN segment is the string 'None'. This is probably a mistake. If it's not, please ignore this warning."
            )
            return segment_str
        if ":" in segment_str:
            raise IllegalArgumentError(
                f"URN identifier [{segment}] cannot contain the ':' character"
            )
        return segment_str

    def is_a(self, cls: Type["SupportsUrn"]) -> bool:  # type: ignore
        v = (
            self.namespace == cls.urn_namespace
            and self.collection == cls.urn_collection
        )
        return v is True

    @property
    def partial_urn(self) -> str:
        return append_segment_to_urn(self.namespace, self.collection)

    @property
    def is_valid(self) -> bool:
        has_encoded_identifier = (
            self.encoded_identifier is not None and len(self.encoded_identifier) > 0
        )
        return has_encoded_identifier and self.encoded_identifier != "None"

    @property
    def identifier(self) -> str:
        return unescaped(self.encoded_identifier)

    @property
    def uuid_identifier(self) -> UUID:
        maybe_uuid = try_uuid(self.encoded_identifier)
        if maybe_uuid is None:
            raise IllegalArgumentError(
                f"URN identifier in [{self}] is not a valid UUID"
            )
        return maybe_uuid

    @property
    def has_uuid(self) -> bool:
        return try_uuid(self.encoded_identifier) is not None

    def __str__(self) -> str:
        return append_segment_to_urn(
            append_segment_to_urn(self.namespace, self.collection),
            self.encoded_identifier,
        )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, RawUrn):
            return False
        if self.namespace != other.namespace or self.collection != other.collection:
            return False
        if self.has_uuid != other.has_uuid:
            return False
        # handle badly encoded urns
        if self.encoded_identifier == "None":
            return other.encoded_identifier == "None"
        if self.has_uuid:
            return self.uuid_identifier == other.uuid_identifier
        else:
            return self.identifier == other.identifier

    def __hash__(self) -> int:
        return hash(str(self))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {str(self)}>"  # urn-ok

    @staticmethod
    # "Use Urn.parse instead"
    def parse_encoded_urn(urn_str: str) -> "Urn":
        return RawUrn.parse(urn_str)

    @staticmethod
    def parse(urn_str: str) -> "Urn":
        if not urn_str:
            raise IllegalArgumentError("URN string cannot be None or empty")
        if not RawUrn.is_valid_as_urn(urn_str):
            raise IllegalArgumentError(f"Invalid URN format: [{urn_str}] is not a URN")
        urn_parts = urn_str.split(":")
        identifier_part = urn_parts[2]
        collection_part = urn_parts[1]
        namespace_part = urn_parts[0]
        if identifier_part == "None":
            return RawUrn.from_raw_identifier(namespace_part, collection_part, None)

        maybe_uuid = try_uuid(identifier_part)
        if not maybe_uuid:
            return RawUrn.from_encoded_identifier(
                namespace_part, collection_part, identifier_part
            )
        else:
            return RawUrn.from_uuid(namespace_part, collection_part, maybe_uuid)

    @staticmethod
    def is_valid_as_urn(urn_str: str) -> bool:
        segments = urn_str.split(":")
        if len(segments) != 3:
            return False
        for segment in segments:
            if not re.match(valid_segment, segment):
                return False
        return True

    @staticmethod
    def maybe_parse_urn(urn_str: Optional[str]) -> Optional["Urn"]:
        if urn_str and RawUrn.is_valid_as_urn(urn_str):
            return RawUrn.parse(urn_str)
        return None

    @classmethod
    def encode_id_for_latest(
        cls, namespace: str, collection: str, identifier: str
    ) -> str:
        return escaped(identifier)

    @classmethod
    def decode_identifier(cls, namespace: str, collection: str, identifier: str) -> str:
        return unescaped(identifier)

    @classmethod
    def from_uuid(cls, namespace: str, collection: str, uuid: UUID) -> "Urn":
        return RawUrn(_urn_secret, namespace, collection, str(uuid))

    @classmethod
    def new_uuid(cls) -> UUID:
        return uuid.uuid4()

    @classmethod
    def random_uuid(cls, namespace: str, collection: str) -> "Urn":
        return cls.from_uuid(namespace, collection, cls.new_uuid())

    @classmethod
    def from_raw_identifier(
        cls, namespace: str, collection: str, identifier: SupportsStr
    ) -> "Urn":
        return Urn.build(namespace, collection, identifier)

    @classmethod
    def build(cls, namespace: str, collection: str, identifier: SupportsStr) -> "Urn":
        identifier = cls._validated_identifier(identifier)
        encoded_id = cls.encode_id_for_latest(namespace, collection, identifier)
        return RawUrn(_urn_secret, namespace, collection, encoded_id)

    @classmethod
    def build_unique(cls, namespace: str, collection: str) -> "Urn":
        return cls.build(namespace, collection, cls.new_uuid())

    @classmethod
    # TODO: Use Urn.build instead
    def from_encoded_identifier(
        cls, namespace: str, collection: str, identifier: SupportsStr
    ) -> "Urn":
        id_str = str(identifier)
        cls.decode_identifier(namespace, collection, id_str)
        return RawUrn(_urn_secret, namespace, collection, id_str)

    @model_serializer
    def ser_model(self) -> str:
        return str(self)


class UrnTypeNotSupportedError(Exception):
    def __init__(self, urn: "Urn", *supported_types: str) -> None:
        super().__init__(
            f"URN [{urn}] is not supported. Supported URNs are: [{supported_types}]"
        )


def urn_for_id(cls: Any, identifier: SupportsStr) -> "Urn":
    if not hasattr(cls, "urn_namespace") or not hasattr(cls, "urn_collection"):
        raise IllegalArgumentError(
            "Provided class does not implement the required SupportsUrn protocol"
            " attributes."
        )
    return RawUrn.from_raw_identifier(cls.urn_namespace, cls.urn_collection, identifier)


def wrap_urn(
    v: Any, handler: ValidatorFunctionWrapHandler, info: ValidationInfo
) -> Any:
    if info.mode == "json":
        assert isinstance(v, str), "In JSON mode the input must be a string!"
        return RawUrn.parse(v)
    assert info.mode == "python"
    if isinstance(v, str):
        return RawUrn.parse(v)
    assert isinstance(
        v, RawUrn
    ), f"In Python mode the input must be an Urn! not a {type(v)} - {v}"
    return v


Urn = Annotated[
    RawUrn,
    WrapValidator(wrap_urn),
]

MaybeUrn = Urn | str


def ensure_urn(urn: MaybeUrn) -> Urn:
    if isinstance(urn, str):
        return RawUrn.parse(urn)
    return urn


def append_segment_to_urn(base: str, segment: str) -> str:
    return f"{base}:{segment}"


def to_urns_list(result: List[str] | str | Urn | List[Urn]) -> List[Urn]:
    if isinstance(result, str):
        return [RawUrn.parse(result)]
    if isinstance(result, RawUrn):
        return [result]
    urn_list = []
    for r in result:
        if isinstance(r, str):
            urn_list.append(RawUrn.parse(r))
        elif isinstance(r, RawUrn):
            urn_list.append(r)
        else:
            raise IllegalArgumentError(f"Invalid type for Urn: {type(r)}")
    return urn_list


def str_to_uuid(value: str) -> uuid.UUID:
    raw = hashlib.sha1(value.encode()).digest()
    return uuid.UUID(bytes=raw[:16])


UrnList = TypeAdapter(list[Urn])

import datetime
import typing as t


class FieldFinder:
    __skip_annotations__: list[str] = ["__skip_annotations__"]

    @classmethod
    def fields(cls) -> t.Iterator[str]:
        for key in cls.__annotations__.keys():
            if key not in cls.__skip_annotations__:
                yield key

    @classmethod
    def as_dict(cls, data: dict[str, str]) -> dict[str, str]:
        """Create a dictionary of the fields associated with this model from an input of key-value
        pairs, without changing the original data.

        Args:
            data (dict[str, str]): the input data (which can have more extra fields than the model)

        Returns:
            dict[str, str]: the key-value pairs of the model data
        """
        return cls.pop_dict(data.copy())

    @classmethod
    def pop_dict(cls, data: dict[str, str]) -> dict[str, str]:
        """Create a dictionary of the fields associated with this model from an input of key-value
        pairs, changing the original data.

        Args:
            data (dict[str, str]): the input data (which can have more extra fields than the model)

        Returns:
            dict[str, str]: the key-value pairs of the model data
        """
        return {key: data.pop(key) for key in cls.fields()}


DATE_FORMATS = ("%m/%d/%Y", "%Y%m%d", "%Y-%m-%d")


def parse_date(value: t.Optional[str]) -> t.Optional[datetime.date]:
    """Parse a date string into its corresponding :py:class:`datetime.date` object by iterating over
    a list of possible formats.

    The list can be found at :py:attr:`DATE_FORMATS`

    Args:
        value (t.Optional[str]): possible date string

    Raises:
        ValueError: Raised when the string cannot be parsed into a datetime object

    Returns:
        t.Optional[datetime.date]: the parsed object
    """
    if value is None:
        return None

    value = str(value)

    for fmt in DATE_FORMATS:
        try:
            return datetime.datetime.strptime(value, fmt).date()

        except ValueError:
            pass

    raise ValueError(f"Could not parse a date value from: {value}")

from datetime import datetime as dt


def iso_format_datetime(datetime: dt) -> str:
    """
    Format datetime to ISO format.

    :param datetime: The datetime to format.
    :return: ISO formatted datetime string.
    """
    return datetime.isoformat(timespec="seconds").replace("+00:00", "Z")

from django import template

register = template.Library()


def _ordinal_suffix(day):
    if 11 <= day % 100 <= 13:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")


def _format_day(day):
    return f"{day.day}{_ordinal_suffix(day.day)}"


@register.simple_tag
def conference_date_range(start_date, end_date):
    if not start_date:
        return ""

    if not end_date:
        end_date = start_date

    if start_date == end_date:
        return f"{start_date.strftime('%B')} {_format_day(start_date)}, {start_date.year}"

    if start_date.year == end_date.year:
        if start_date.month == end_date.month:
            return (
                f"{start_date.strftime('%B')} {_format_day(start_date)} to "
                f"{_format_day(end_date)}, {start_date.year}"
            )
        return (
            f"{start_date.strftime('%B')} {_format_day(start_date)} to "
            f"{end_date.strftime('%B')} {_format_day(end_date)}, {start_date.year}"
        )

    return (
        f"{start_date.strftime('%B')} {_format_day(start_date)}, {start_date.year} to "
        f"{end_date.strftime('%B')} {_format_day(end_date)}, {end_date.year}"
    )

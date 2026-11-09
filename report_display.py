"""Editorial display only; never feed these values into bands or matching."""
from decimal import Decimal, ROUND_HALF_UP


def ten_point_score(raw):
    """Uniform monotone scale: raw 45 -> 3 and 65 -> 7; five raw points per step.

    Decimal keeps exact half-step boundaries stable. Values are symbolic,
    not percentiles, probabilities, or measured relationship quality.
    """
    value = Decimal(4) + (Decimal(str(raw)) - 50) / 5
    return max(1, min(10, int(value.quantize(Decimal(1), rounding=ROUND_HALF_UP))))


def reduce_body_bold(value):
    """Preserve heading lines and every character of prose except ** markers."""
    return '\n'.join(line if line.lstrip().startswith(('◆ ', '#'))
                     else line.replace('**', '') for line in value.split('\n'))

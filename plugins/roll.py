"""
:Date: 2016-09-05
:Version: 0.0.1
:Author:
    - Jackson McCrea (jacksonmccrea@gmail.com)
"""

from random import shuffle
from guilty_spark.plugin_system.dynamic import Dynamic, DynamicError

dyn = Dynamic()


@dyn.command()
def roll(number):
    """Roll the dice!"""

    try:
        number = int(number)
    except ValueError:
        raise DynamicError('Only numbers are allowed')

    outcomes = [i for i in range(1, number)]
    for _ in range(20):
        shuffle(outcomes)

    return str(outcomes[0])

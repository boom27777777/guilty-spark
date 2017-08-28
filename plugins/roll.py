"""
:Date: 2016-09-05
:Version: 0.0.1
:Author:
    - Jackson McCrea (jacksonmccrea@gmail.com)
"""

from random import shuffle, randint
from guilty_spark.plugin_system.dynamic import Dynamic, DynamicError

dyn = Dynamic()


@dyn.command()
def roll(number):
    """Roll the dice! """

    try:
        number = int(number)
    except ValueError:
        raise DynamicError('Only numbers are allowed')

    if number <= 0:
        raise DynamicError('Only 1 and higher numbers are allowed')

    if number > 1000:
        result = randint(1, number)

    else:
        outcomes = [i for i in range(1, number + 1)]
        for _ in range(20):
            shuffle(outcomes)
        result = outcomes[0]

    return str(result)

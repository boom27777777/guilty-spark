"""
:Date: 2016-09-05
:Version: 0.0.1
:Author:
    - Jackson McCrea (jacksonmccrea@gmail.com)
"""

import re

from random import shuffle, randint
from guilty_spark.plugin_system.dynamic import Dynamic, DynamicError

dyn = Dynamic()

# example 1d6+1
die_pattern = regex = r'([0-9]+)d([0-9]+)(?:([+-])([0-9]+))?'

@dyn.command()
async def roll(value):
    """Roll the dice!
        
    Supports the normal dice rolling syntax. 
    For example: 1d6 would roll 1 6 sided die.
    Also supports modifiers, positive and negitive: 1d6+2
    """

    try:
        num_rolls, die, mod, mod_value = re.findall(die_pattern, value)[0]
    except:
        raise
    
    try:
        number = int(die)
        rolls = int(num_rolls)
        if mod:
            mod_value = int(mod_value)
        else:
            mod = '+'
            mod_value = 0

    except ValueError:
        raise DynamicError('Only numbers are allowed for the die (for example: 1d6)')

    if number <= 0:
        raise DynamicError('Only 1 and higher numbers are allowed')

    results = []

    if rolls > 100:
        raise DynamicError('I can only roll 100 dice at a time.')

    for _ in range(rolls):
        result = randint(1, number)
        results.append(result)

    if mod == "-":
        mod_value *= -1

    return str("Total: {} ({}) {} {}".format(
        sum(results) + mod_value, 
        ', '.join([str(i) for i in results]), 
        mod, 
        abs(mod_value)
    ))

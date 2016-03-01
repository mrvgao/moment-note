'''
Defines some customed functions for functional programming.

Author: Minchiuan Gao 2016-Mar-1
'''


def reduce(function, iterable, initializer=None):
    '''
    Rewrite the system reduce. To be more suitable.
    '''

    it = iter(iterable)
    if initializer is None:
        try:
            initializer = next(it)
        except StopIteration:
            raise TypeError('reduce() of empty sequence with no initial value')

    accum_value = initializer
    for x in it:
        function(accum_value, x)

    return accum_value

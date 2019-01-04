from i2i.pymint import mint_of_callable


def test_callable(arg1, arg2: int) -> str:
    """
    A testable callable.
    :param str arg1: A string
    """

    print('calling!')
    print(arg1)
    print(arg2)
    return 'returned'


minted = mint_of_callable(test_callable)

print(str(minted), type(minted))

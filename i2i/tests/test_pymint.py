def test_func_1(any_var, an_int: int, a_float, a_bool: bool, a_str, a_list: list, a_dict: dict) -> str:
    """
    This is the first line,
    continued on the next.

    And this is some more information about the function:
    Blah
    Blah
    Bloo

    :param any_var: this can be of any type
    :param an_int: an int
    :param float a_float: a float
    :param a_bool: a bool
    :param a_str: a str
    :param a_list:
    :param a_dict: An example of a continued
    line description
    :return str: Will just return the 'test_func_1 returned' string
    :tags foo, bar
    >>> # here are sometests
    >>> test_func_1('anything', 1, 1.1, True, 'hello', [1, 2], {'this': 0, 'that': 'foo'})
    'returned'
    """
    return 'test_func_1 returned'


class SomeClass(object):
    pass


class SomeOtherClass(object):
    pass


def test_func_2(any_var, an_int: int, a_float: 0.1, a_tuple: tuple = (),
                an_obj: SomeClass = SomeClass(), another_obj=SomeOtherClass()):
    """
    This is the first line,
    continued on the next.

    And this is some more information about the function:
    Blah
    Blah
    Bloo

    :param any_var: foo
    :param an_int: you again?!
    :param a_float:
    :param a_tuple: For real
    :param an_obj: Does nothing
    :param another_obj: Multi-
    line
    :return: Just pi
    :tags any, old, tag
    :keyword one_keyword
    :keyword keyword1, keyword2
    """

    """
    This is the first line,
    continued on the next.

    And this is some more information about the function:
    Blah
    Blah
    Bloo

    :param any_var: this can be of any type
    :param an_int: an int
    :param a_float: a float
    :param a_bool: a bool
    :param a_str: a str
    :param a_list:
    :param a_dict: An example of a continued
    line description
    :return:
    >>> # here are sometests
    >>> test_func_1('anything', 1, 1.1, True, 'hello', [1, 2], {'this': 0, 'that': 'foo'})
    'returned'
    """
    return 3.14

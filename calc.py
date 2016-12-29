"""
Parse tsv of
'description \t amount'
"""
import sys
import functools
import pprint

class EmptyLine(object):
    """
    Object to signal the presence of a line consisting of blankspace only
    """
    pass


class LegalException(Exception):
    pass
class IllegalException(Exception):
    pass


class EmptyLineException(LegalException):
    pass
class WrongLineFormatException(IllegalException):
    pass
class NoAmountException(WrongLineFormatException):
    pass
class IllegalAmountException(WrongLineFormatException):
    pass


def trav_file(file_name):
    k = 1
    with open(file_name) as f:
        for line in f:
            yield k, line
            k += 1


def calc_line(line):
    """
    Attempts parsing line to amount and
    returning the amount*100
    """
    if type(line) is not str:
        raise TypeError("Line must be of type str")
    if len(line.split()) == 0:
        raise EmptyLineException("This line is empty")

    parts = line.split("\t")
    if len(parts) == 0:
        raise EmptyLineException("This line is empty")
    elif len(parts) == 1:
        raise NoAmountException("Line '{}' should be of form '_title_ _TAB_ _amount_'".format(line))
    elif len(parts) > 2:
        raise WrongLineFormatException("Line '{}' should be of form '_title_ _TAB_ _amount_'".format(line))

    #parts has length == 2:
    amounts = parts[1].split(",")
    if len(amounts) < 3:
        amount_whole = int(amounts[0])
        if len(amounts) == 2:
            amount_frac = int(amounts[1])
        else:
            amount_frac = 0
    else:
        raise IllegalAmountException("Illegal amount provided for line '{}'".format(line))
    
    return amount_whole*100 + amount_frac


def error_printer(line_num, e):
    print("Exception at line {}:".format(line_num))
    print(str(type(e)) +"\n\n", e)
    
    
def parse_line(line, line_num):
    try:
        amount = calc_line(line)
    except EmptyLineException as ele:
        return 0, [(line_num, EmptyLine())]
    except IllegalException as ie:
        error_printer(line_num, ie)
        sys.exit(1)
    except ValueError as ve:
        error_printer(line_num, ve)
        sys.exit(1)
    except Exception as e:
        raise e
        sys.exit(1)
    return amount, []


def parser(line_num, line):
    return parse_line(line, line_num)


class Summary(object):

    def __init__(self, amount, legal_exceptions=[]):
        self.amount = amount
        self.legal_exceptions = legal_exceptions

    def __add__(self, other):
        new_legal_exceptions = []
        new_legal_exceptions.extend(self.legal_exceptions)
        new_legal_exceptions.extend(other.legal_exceptions)
        return Summary(
            self.amount+other.amount,
            new_legal_exceptions
        )

    def get_amounts(self):
        return "{}.{}".format(self.amount//100, self.amount % 100)
        
    def __str__(self):
        s = "Amount is {}\n".format(self.get_amounts())
        s += "Admittable exceptions are:\n"
        s += pprint.pformat(self.legal_exceptions)
        return s



def get_summary(line_iter):
    return functools.reduce(
        lambda s, am_exc: (s + Summary(am_exc[0], am_exc[1])),
        map(lambda l: parser(l[0], l[1]), line_iter),
        Summary(0, [])
    )
 


if __name__ == "__main__":
    print(
        "\n" +
        str(get_summary(trav_file(sys.argv[1]))) +
        "\n"
    )

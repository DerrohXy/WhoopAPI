import pprint


def LOG_INFO(*args):
    return print(*args)


def LOG_WARNING(*args):
    return print(*args)


def LOG_ERROR(*args):
    return print(*args)


def LOG_CRITICAL(*args):
    return print(*args)


def LOG_PRETTY(*args):
    return pprint.pprint(*args)

#!/bin/env python


import click
import importlib
import inspect
import logging
from pprint import pprint


log = logging.getLogger('pymdgen')


def doc_func(name, func, section_level=4):
    docstr = inspect.getdoc(func)
    # skip functions without a docstr
    if not docstr:
        return

    spec = inspect.getargspec(func)
    display = []
    end_args = []

    # *args and **kwargs
    if spec[1]:
        end_args.append('*' + spec[1])
    if spec[2]:
        end_args.append('**' + spec[2])

    # check for args with defaults
    if spec[3]:
        args = spec[0][-len(spec[3]):]
        default_args = list(zip(args, spec[3]))

        # set args to rest
        args = spec[0][:-len(spec[3])]
    else:
        args = spec[0]
        default_args = []

    if args:
        display.append(', '.join(args))
    if default_args:
        display.append(', '.join('%s=%s' % x for x in default_args))
    if end_args:
        display.append(', '.join(end_args))

    print('#' * section_level, name)
    print()
    print('```')
    print(name + '(' + ', '.join(display) + ')')
    print('```')
    print()
    print(docstr)
    print()


def doc_class(name, cls, section_level=3):
    docstr = inspect.getdoc(cls)
    # skip functions without a docstr
    if not docstr:
        return

    # full mro is probably overkill?
    # base_classes = inspect.getmro(cls)
    base_classes = cls.__bases__
    base_classes = (c.__module__ + '.' + c.__name__ for c in base_classes)

    print('#' * section_level, name)
    print()
    print('```')
    print(name + '(' + ', '.join(base_classes) + ')')
    print('```')
    print()
    print(docstr)
    print()

    for name, func in list(cls.__dict__.items()):
        if inspect.isfunction(func):
            doc_func(name, func, section_level + 1)

    print()


@click.command()
@click.option('--debug', help='display debug messages', is_flag=True, default=False)
@click.option('--section-level', help='markdown section level', default=3)
@click.argument('modules', nargs=-1)
def main(modules, debug, section_level):
    """ inspects given python modules and prints markdown """

    if debug:
        logging.basicConfig(level=logging.DEBUG)

    for name in modules:
        if '/' in name or name.endswith('.py'):
            name = name.replace('/', '.')
            name = name.rstrip('.py')
            print('modules should be in python notation, trying with', name)

        module = importlib.import_module(name)

        for k, v in inspect.getmembers(module):
            if k == '__builtins__':
                continue
            log.debug("checking %s:%s" % (v, k))
            if inspect.isfunction(v):
                doc_func(k, v, section_level)
            if inspect.isclass(v):
                doc_class(k, v, section_level)

if __name__ == "__main__":
    main()


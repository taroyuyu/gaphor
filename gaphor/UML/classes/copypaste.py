import itertools

from gaphor.diagram.copypaste import copy, copy_named_element
from gaphor.UML import Association, Class, Interface, Operation


@copy.register(Class)
@copy.register(Interface)
def copy_class(element):
    yield element.id, copy_named_element(element)
    for feature in itertools.chain(
        element.ownedAttribute,
        element.ownedOperation,
    ):
        yield from copy(feature)


@copy.register
def copy_operation(element: Operation):
    yield element.id, copy_named_element(element)
    for feature in element.ownedParameter:
        yield from copy(feature)


@copy.register
def copy_association(element: Association):
    yield element.id, copy_named_element(element)
    for end in element.memberEnd:
        yield from copy(end)

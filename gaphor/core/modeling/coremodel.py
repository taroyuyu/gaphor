# This file is generated by codegen.py. DO NOT EDIT!

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Callable, List, Optional

from gaphor.core.modeling.element import Element
from gaphor.core.modeling.properties import (
    association,
    attribute,
    derived,
    derivedunion,
    enumeration,
    redefine,
    relation_many,
    relation_one,
)

if TYPE_CHECKING:
    from gaphor.UML import Component, Dependency, Namespace, Package
# 8: override Element
# defined above


# 11: override NamedElement
# Define extra attributes defined in UML model
class NamedElement(Element):
    name: attribute[str]
    qualifiedName: derived[List[str]]
    visibility: enumeration
    namespace: relation_one[Namespace]
    clientDependency: relation_many[Dependency]
    supplierDependency: relation_many[Dependency]
    memberNamespace: relation_many[Namespace]


# 39: override PackageableElement
class PackageableElement(NamedElement):
    owningPackage: relation_one[Package]
    component: relation_one[Component]


# 67: override Diagram
# defined in gaphor.core.modeling.diagram


# 49: override Presentation
# defined in gaphor.core.modeling.presentation


class Comment(Element):
    body: attribute[str]
    annotatedElement: relation_many[Element]


# 43: override StyleSheet
# defined in gaphor.core.modeling.presentation


NamedElement.name = attribute("name", str)
Comment.body = attribute("body", str)
# 46: override StyleSheet.styleSheet
# defined in gaphor.core.modeling.presentation

# 58: override Presentation.subject
# defined in gaphor.core.modeling.presentation

# 52: override Element.presentation
# defined in gaphor.core.modeling.presentation

Comment.annotatedElement = association("annotatedElement", Element, opposite="comment")
Element.comment = association("comment", Comment, opposite="annotatedElement")
# 70: override Diagram.ownedPresentation
# defined in gaphor.core.modeling.presentation

# 55: override Presentation.diagram
# defined in gaphor.core.modeling.presentation

# 61: override Presentation.parent
# defined in gaphor.core.modeling.presentation

# 64: override Presentation.children
# defined in gaphor.core.modeling.presentation

# 22: override NamedElement.qualifiedName(NamedElement.namespace): derived[List[str]]


def _namedelement_qualifiedname(self) -> List[str]:
    """Returns the qualified name of the element as a tuple."""
    if self.namespace:
        return _namedelement_qualifiedname(self.namespace) + [self.name]
    else:
        return [self.name]


NamedElement.qualifiedName = derived(
    "qualifiedName",
    List[str],
    0,
    1,
    lambda obj: [_namedelement_qualifiedname(obj)],
)

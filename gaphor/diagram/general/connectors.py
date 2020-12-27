"""Connect comments."""

import logging
from typing import Union

from gaphor.core.modeling import Comment
from gaphor.diagram.connectors import BaseConnector, Connector
from gaphor.diagram.general.comment import CommentItem
from gaphor.diagram.general.commentline import CommentLineItem
from gaphor.diagram.presentation import ElementPresentation, LinePresentation

logger = logging.getLogger(__name__)


@Connector.register(CommentItem, CommentLineItem)
@Connector.register(ElementPresentation, CommentLineItem)
@Connector.register(LinePresentation, CommentLineItem)
class CommentLinePresentationConnect(BaseConnector):
    """Connect a comment line to any element item."""

    element: Union[CommentItem, ElementPresentation, LinePresentation]
    line: CommentLineItem

    def allow(self, handle, port):
        """In addition to the normal check, both line ends may not be connected
        to the same element.

        Same goes for subjects. One of the ends should be connected to a
        Comment element.
        """
        opposite = self.line.opposite(handle)
        connected_to = self.get_connected(opposite)
        element = self.element

        if connected_to is element:
            return None

        # Same goes for subjects:
        if (
            connected_to
            and not connected_to.subject
            and not element.subject
            and connected_to.subject is element.subject
        ):
            return None

        # One end should be connected to a CommentItem:
        cls = CommentItem
        glue_ok = isinstance(connected_to, cls) ^ isinstance(self.element, cls)
        if connected_to and not glue_ok:
            return None

        return super().allow(handle, port)

    def connect(self, handle, port):
        if super().connect(handle, port):
            opposite = self.line.opposite(handle)
            connected_to = self.get_connected(opposite)
            if connected_to and connected_to.subject and self.element.subject:
                if isinstance(connected_to.subject, Comment):
                    connected_to.subject.annotatedElement = self.element.subject
                else:
                    assert isinstance(self.element.subject, Comment)
                    self.element.subject.annotatedElement = connected_to.subject

    def disconnect(self, handle):
        opposite_handle = self.line.opposite(handle)
        opposite = self.get_connected(opposite_handle)
        element = self.element

        if element and element.subject and opposite and opposite.subject:
            comment_line_items_1 = set(all_comment_line_items(element.subject))
            comment_line_items_2 = set(all_comment_line_items(opposite.subject))
            if len(comment_line_items_1.intersection(comment_line_items_2)) > 1:
                return

            logger.debug("Disconnecting %s and %s", element, opposite)
            if isinstance(opposite.subject, Comment):
                del opposite.subject.annotatedElement[element.subject]
            elif opposite.subject:
                assert isinstance(element.subject, Comment)
                del element.subject.annotatedElement[opposite.subject]

        super().disconnect(handle)


def all_comment_line_items(subject):
    for presentation in subject.presentation:
        connections = presentation.diagram.connections
        for cinfo in connections.get_connections(connected=presentation):
            if isinstance(cinfo.item, CommentLineItem):
                yield cinfo.item


@Connector.register(CommentLineItem, LinePresentation)
class InverseCommentLineLineConnect(CommentLinePresentationConnect):
    """In case a line is disconnected that contains a comment-line, the comment
    line unlinking should happen in a correct way."""

    def __init__(self, line, element):
        super().__init__(element, line)

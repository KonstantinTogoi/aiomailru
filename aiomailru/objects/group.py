from collections import UserDict


class GroupItem(UserDict):
    """Group item."""

    def __init__(self, initialdata):
        super().__init__(initialdata)

    def __repr__(self):
        return repr(self.data)

    @classmethod
    async def from_element(cls, element):
        """Creates a new group item from a DOM element.

        Args:
            element (pyppeteer.element_handle.ElementHandle): the element.

        Returns:
            item (GroupItem): new instance of this class.

        """

        pass

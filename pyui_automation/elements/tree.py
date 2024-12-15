from typing import Optional, Any, List
from .base import UIElement


class TreeNode(UIElement):
    """Represents a tree node element"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def text(self) -> str:
        """
        Get the text of the tree node.

        Returns:
            str: Node text
        """
        return self._element.get_property("text")

    @property
    def is_expanded(self) -> bool:
        """
        Check if the node is expanded.

        Returns:
            bool: True if expanded, False otherwise
        """
        return self._element.get_property("expanded")

    @property
    def is_selected(self) -> bool:
        """
        Check if the node is selected.

        Returns:
            bool: True if selected, False otherwise
        """
        return self._element.get_property("selected")

    @property
    def level(self) -> int:
        """
        Get the nesting level of the node.

        Returns:
            int: Nesting level (0 for root)
        """
        return self._element.get_property("level")

    @property
    def has_children(self) -> bool:
        """
        Check if the node has child nodes.

        Returns:
            bool: True if has children, False otherwise
        """
        return self._element.get_property("has_children")

    def expand(self) -> None:
        """Expand the node if it has children and is not already expanded"""
        if self.has_children and not self.is_expanded:
            self.click()

    def collapse(self) -> None:
        """Collapse the node if it has children and is expanded"""
        if self.has_children and self.is_expanded:
            self.click()

    def select(self) -> None:
        """Select the node"""
        if not self.is_selected:
            self.click()

    def get_parent(self) -> Optional['TreeNode']:
        """
        Get the parent node.

        Returns:
            Optional[TreeNode]: Parent node or None if root
        """
        if self.level == 0:
            return None
        parent = self._element.find_element(by="parent", value=None)
        return TreeNode(parent, self._session) if parent else None

    def get_children(self) -> List['TreeNode']:
        """
        Get all child nodes.

        Returns:
            List[TreeNode]: List of child nodes
        """
        if not self.has_children:
            return []
        if not self.is_expanded:
            self.expand()
        children = self._element.find_elements(by="children", value=None)
        return [TreeNode(child, self._session) for child in children]

    def wait_until_expanded(self, timeout: float = 10) -> bool:
        """
        Wait until the node becomes expanded.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if node became expanded within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.is_expanded,
            timeout=timeout,
            error_message="Node did not become expanded"
        )

    def wait_until_collapsed(self, timeout: float = 10) -> bool:
        """
        Wait until the node becomes collapsed.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if node became collapsed within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: not self.is_expanded,
            timeout=timeout,
            error_message="Node did not become collapsed"
        )


class TreeView(UIElement):
    """Represents a tree view control element"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def root_nodes(self) -> List[TreeNode]:
        """
        Get all root nodes in the tree.

        Returns:
            List[TreeNode]: List of root nodes
        """
        nodes = self._element.find_elements(by="level", value=0)
        return [TreeNode(node, self._session) for node in nodes]

    def get_node_by_path(self, path: List[str]) -> Optional[TreeNode]:
        """
        Find a node by its path from root.

        Args:
            path (List[str]): List of node texts from root to target

        Returns:
            Optional[TreeNode]: Found node or None if not found
        """
        if not path:
            return None

        current_nodes = self.root_nodes
        current_node = None

        for node_text in path:
            found = False
            for node in current_nodes:
                if node.text == node_text:
                    current_node = node
                    if not node.is_expanded:
                        node.expand()
                    current_nodes = node.get_children()
                    found = True
                    break
            if not found:
                return None

        return current_node

    def get_selected_nodes(self) -> List[TreeNode]:
        """
        Get all currently selected nodes.

        Returns:
            List[TreeNode]: List of selected nodes
        """
        nodes = self._element.find_elements(by="state", value="selected")
        return [TreeNode(node, self._session) for node in nodes]

    def expand_all(self) -> None:
        """Expand all nodes in the tree"""
        def expand_recursive(node: TreeNode):
            if node.has_children and not node.is_expanded:
                node.expand()
                for child in node.get_children():
                    expand_recursive(child)

        for root in self.root_nodes:
            expand_recursive(root)

    def collapse_all(self) -> None:
        """Collapse all nodes in the tree"""
        def collapse_recursive(node: TreeNode):
            if node.has_children:
                for child in node.get_children():
                    collapse_recursive(child)
                if node.is_expanded:
                    node.collapse()

        for root in self.root_nodes:
            collapse_recursive(root)

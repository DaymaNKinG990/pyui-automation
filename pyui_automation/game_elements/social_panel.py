from typing import Optional, Any, Dict, List, Tuple
from datetime import datetime
from ..elements.base import UIElement


class Friend(UIElement):
    """Represents a friend in the friends list"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def name(self) -> str:
        """Get friend name"""
        return self._element.get_property("name")

    @property
    def level(self) -> int:
        """Get friend level"""
        return self._element.get_property("level")

    @property
    def class_name(self) -> str:
        """Get friend class"""
        return self._element.get_property("class")

    @property
    def status(self) -> str:
        """Get online status"""
        return self._element.get_property("status")

    @property
    def location(self) -> Optional[str]:
        """Get current location if online"""
        return self._element.get_property("location")

    @property
    def note(self) -> str:
        """Get friend note"""
        return self._element.get_property("note")

    @property
    def is_online(self) -> bool:
        """Check if friend is online"""
        return self.status != "offline"

    def whisper(self, message: str) -> bool:
        """
        Send whisper message

        Args:
            message (str): Message to send

        Returns:
            bool: True if successful
        """
        whisper_button = self._element.find_element(by="type", value="whisper_button")
        if whisper_button:
            whisper_button.click()
            chat_input = self._element.find_element(by="type", value="chat_input")
            if chat_input:
                chat_input.send_keys(message)
                chat_input.send_keys("\n")
                return True
        return False

    def invite_group(self) -> bool:
        """
        Invite friend to group

        Returns:
            bool: True if invite sent
        """
        invite_button = self._element.find_element(by="type", value="invite_button")
        if invite_button and invite_button.is_enabled():
            invite_button.click()
            return True
        return False

    def remove(self) -> bool:
        """
        Remove from friends list

        Returns:
            bool: True if successful
        """
        remove_button = self._element.find_element(by="type", value="remove_button")
        if remove_button:
            remove_button.click()
            confirm_button = self._element.find_element(by="type", value="confirm_remove")
            if confirm_button:
                confirm_button.click()
                return True
        return False

    def set_note(self, note: str) -> bool:
        """
        Set friend note

        Args:
            note (str): Note text

        Returns:
            bool: True if successful
        """
        note_button = self._element.find_element(by="type", value="note_button")
        if note_button:
            note_button.click()
            note_input = self._element.find_element(by="type", value="note_input")
            if note_input:
                note_input.send_keys(note)
                note_input.send_keys("\n")
                return True
        return False


class Block(UIElement):
    """Represents a blocked player"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def name(self) -> str:
        """Get blocked player name"""
        return self._element.get_property("name")

    @property
    def reason(self) -> Optional[str]:
        """Get block reason"""
        return self._element.get_property("reason")

    @property
    def block_time(self) -> datetime:
        """Get when player was blocked"""
        return self._element.get_property("block_time")

    def unblock(self) -> bool:
        """
        Unblock player

        Returns:
            bool: True if successful
        """
        unblock_button = self._element.find_element(by="type", value="unblock_button")
        if unblock_button:
            unblock_button.click()
            return True
        return False


class SocialPanel(UIElement):
    """Represents the social panel interface"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def friend_count(self) -> Tuple[int, int]:
        """Get current and maximum friend count"""
        return (
            self._element.get_property("current_friends"),
            self._element.get_property("max_friends")
        )

    @property
    def online_count(self) -> int:
        """Get number of online friends"""
        return self._element.get_property("online_count")

    def get_friends(self, online_only: bool = False) -> List[Friend]:
        """
        Get friends list

        Args:
            online_only (bool): Only return online friends

        Returns:
            List[Friend]: List of friends
        """
        friends = self._element.find_elements(
            by="type",
            value="friend",
            online=online_only
        )
        return [Friend(f, self._session) for f in friends]

    def get_friend(self, name: str) -> Optional[Friend]:
        """
        Find friend by name

        Args:
            name (str): Friend name

        Returns:
            Optional[Friend]: Found friend or None
        """
        friend = self._element.find_element(
            by="type",
            value="friend",
            name=name
        )
        return Friend(friend, self._session) if friend else None

    def get_blocks(self) -> List[Block]:
        """
        Get blocked players list

        Returns:
            List[Block]: List of blocks
        """
        blocks = self._element.find_elements(by="type", value="block")
        return [Block(b, self._session) for b in blocks]

    def add_friend(self, player_name: str) -> bool:
        """
        Add player to friends list

        Args:
            player_name (str): Player name to add

        Returns:
            bool: True if successful
        """
        add_button = self._element.find_element(by="type", value="add_friend")
        if add_button:
            add_button.click()
            name_input = self._element.find_element(by="type", value="player_name")
            if name_input:
                name_input.send_keys(player_name)
                name_input.send_keys("\n")
                return True
        return False

    def block_player(self, player_name: str, reason: Optional[str] = None) -> bool:
        """
        Block player

        Args:
            player_name (str): Player name to block
            reason (Optional[str]): Block reason

        Returns:
            bool: True if successful
        """
        block_button = self._element.find_element(by="type", value="block_player")
        if block_button:
            block_button.click()
            name_input = self._element.find_element(by="type", value="player_name")
            if name_input:
                name_input.send_keys(player_name)
                if reason:
                    reason_input = self._element.find_element(by="type", value="reason")
                    if reason_input:
                        reason_input.send_keys(reason)
                name_input.send_keys("\n")
                return True
        return False

    def search_friends(self, query: str) -> List[Friend]:
        """
        Search friends list

        Args:
            query (str): Search query

        Returns:
            List[Friend]: List of matching friends
        """
        search_box = self._element.find_element(by="type", value="search")
        if search_box:
            search_box.send_keys(query)

        results = self._element.find_elements(by="type", value="search_result")
        return [Friend(r, self._session) for r in results]

    def broadcast_message(self, message: str) -> bool:
        """
        Send message to all online friends

        Args:
            message (str): Message to send

        Returns:
            bool: True if successful
        """
        broadcast_button = self._element.find_element(by="type", value="broadcast")
        if broadcast_button:
            broadcast_button.click()
            message_input = self._element.find_element(by="type", value="message_input")
            if message_input:
                message_input.send_keys(message)
                message_input.send_keys("\n")
                return True
        return False

    def wait_for_friend_online(self, name: str, timeout: float = 10) -> bool:
        """
        Wait for friend to come online

        Args:
            name (str): Friend name
            timeout (float): Maximum wait time in seconds

        Returns:
            bool: True if friend came online within timeout
        """
        def check_online():
            friend = self.get_friend(name)
            return friend and friend.is_online

        return self._session.wait_for_condition(
            check_online,
            timeout=timeout,
            error_message=f"Friend '{name}' did not come online"
        )

    def wait_for_friend_offline(self, name: str, timeout: float = 10) -> bool:
        """
        Wait for friend to go offline

        Args:
            name (str): Friend name
            timeout (float): Maximum wait time in seconds

        Returns:
            bool: True if friend went offline within timeout
        """
        def check_offline():
            friend = self.get_friend(name)
            return friend and not friend.is_online

        return self._session.wait_for_condition(
            check_offline,
            timeout=timeout,
            error_message=f"Friend '{name}' did not go offline"
        )

    def send_whisper(self, player_name: str, message: str) -> bool:
        """
        Send whisper message to player
        
        Args:
            player_name (str): Player to whisper to
            message (str): Message to send
        
        Returns:
            bool: True if successful
        """
        friend = self.get_friend(player_name)
        if friend:
            return friend.whisper(message)
        return False

    def invite_to_group(self, player_name: str) -> bool:
        """
        Invite player to group
        
        Args:
            player_name (str): Player to invite
        
        Returns:
            bool: True if successful
        """
        friend = self.get_friend(player_name)
        if friend:
            return friend.invite_group()
        return False

    def is_friend_online(self, friend_name: str) -> bool:
        """
        Check if friend is online
        
        Args:
            friend_name (str): Friend to check
        
        Returns:
            bool: True if friend is online
        """
        friend = self.get_friend(friend_name)
        return friend.is_online if friend else False

    def get_blocked_players(self) -> List[Block]:
        """
        Get list of blocked players
        
        Returns:
            List[Block]: List of blocked players
        """
        return self.get_blocks()

    def remove_friend(self, friend_name: str) -> bool:
        """
        Remove friend from friends list
        
        Args:
            friend_name (str): Friend to remove
        
        Returns:
            bool: True if successful
        """
        friend = self.get_friend(friend_name)
        if friend:
            return friend.remove()
        return False

    def unblock_player(self, player_name: str) -> bool:
        """
        Unblock a player
        
        Args:
            player_name (str): Player to unblock
        
        Returns:
            bool: True if successful
        """
        blocks = self.get_blocks()
        for block in blocks:
            if block.name == player_name:
                return block.unblock()
        return False
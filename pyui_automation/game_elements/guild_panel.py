from typing import Optional, Any, Dict, List, Tuple
from datetime import datetime
from ..elements.base import UIElement


class GuildMember(UIElement):
    """Represents a guild member"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def name(self) -> str:
        """Get member name"""
        return self._element.get_property("name")

    @property
    def rank(self) -> str:
        """Get member rank"""
        return self._element.get_property("rank")

    @property
    def level(self) -> int:
        """Get member level"""
        return self._element.get_property("level")

    @property
    def class_name(self) -> str:
        """Get member class"""
        return self._element.get_property("class")

    @property
    def note(self) -> str:
        """Get member note"""
        return self._element.get_property("note")

    @property
    def last_online(self) -> datetime:
        """Get last online timestamp"""
        return self._element.get_property("last_online")

    @property
    def is_online(self) -> bool:
        """Check if member is online"""
        return self._element.get_property("online")

    def promote(self) -> bool:
        """
        Promote member to next rank

        Returns:
            bool: True if successful
        """
        promote_button = self._element.find_element(by="type", value="promote_button")
        if promote_button and promote_button.is_enabled():
            promote_button.click()
            return True
        return False

    def demote(self) -> bool:
        """
        Demote member to previous rank

        Returns:
            bool: True if successful
        """
        demote_button = self._element.find_element(by="type", value="demote_button")
        if demote_button and demote_button.is_enabled():
            demote_button.click()
            return True
        return False

    def kick(self) -> bool:
        """
        Kick member from guild

        Returns:
            bool: True if successful
        """
        kick_button = self._element.find_element(by="type", value="kick_button")
        if kick_button and kick_button.is_enabled():
            kick_button.click()
            confirm_button = self._element.find_element(by="type", value="confirm_kick")
            if confirm_button:
                confirm_button.click()
                return True
        return False

    def set_note(self, note: str) -> bool:
        """
        Set member note

        Args:
            note (str): New note text

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


class GuildRank(UIElement):
    """Represents a guild rank"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def name(self) -> str:
        """Get rank name"""
        return self._element.get_property("name")

    @property
    def permissions(self) -> List[str]:
        """Get rank permissions"""
        return self._element.get_property("permissions") or []

    def rename(self, new_name: str) -> bool:
        """
        Rename the rank

        Args:
            new_name (str): New rank name

        Returns:
            bool: True if successful
        """
        name_field = self._element.find_element(by="type", value="rank_name")
        if name_field:
            name_field.send_keys(new_name)
            name_field.send_keys("\n")
            return True
        return False

    def set_permission(self, permission: str, enabled: bool) -> bool:
        """
        Set rank permission

        Args:
            permission (str): Permission name
            enabled (bool): Enable or disable

        Returns:
            bool: True if successful
        """
        perm_checkbox = self._element.find_element(
            by="type",
            value="permission",
            name=permission
        )
        if perm_checkbox:
            if perm_checkbox.is_checked() != enabled:
                perm_checkbox.click()
            return True
        return False


class GuildPanel(UIElement):
    """Represents the guild management interface"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def name(self) -> str:
        """Get guild name"""
        return self._element.get_property("name")

    @property
    def level(self) -> int:
        """Get guild level"""
        return self._element.get_property("level")

    @property
    def member_count(self) -> Tuple[int, int]:
        """Get current and maximum member count"""
        return (
            self._element.get_property("current_members"),
            self._element.get_property("max_members")
        )

    @property
    def motd(self) -> str:
        """Get message of the day"""
        return self._element.get_property("motd")

    @property
    def ranks(self) -> List[GuildRank]:
        """Get all guild ranks"""
        ranks = self._element.find_elements(by="type", value="guild_rank")
        return [GuildRank(r, self._session) for r in ranks]

    def get_members(self, rank: Optional[str] = None) -> List[GuildMember]:
        """
        Get guild members, optionally filtered by rank

        Args:
            rank (Optional[str]): Filter by rank name

        Returns:
            List[GuildMember]: List of members
        """
        members = self._element.find_elements(
            by="type",
            value="guild_member",
            rank=rank
        )
        return [GuildMember(m, self._session) for m in members]

    def get_member(self, name: str) -> Optional[GuildMember]:
        """
        Find member by name

        Args:
            name (str): Member name

        Returns:
            Optional[GuildMember]: Found member or None
        """
        member = self._element.find_element(
            by="type",
            value="guild_member",
            name=name
        )
        return GuildMember(member, self._session) if member else None

    def get_rank(self, name: str) -> Optional[GuildRank]:
        """
        Find rank by name

        Args:
            name (str): Rank name

        Returns:
            Optional[GuildRank]: Found rank or None
        """
        for rank in self.ranks:
            if rank.name == name:
                return rank
        return None

    def set_motd(self, message: str) -> bool:
        """
        Set message of the day

        Args:
            message (str): New message

        Returns:
            bool: True if successful
        """
        motd_button = self._element.find_element(by="type", value="motd_button")
        if motd_button:
            motd_button.click()
            motd_input = self._element.find_element(by="type", value="motd_input")
            if motd_input:
                motd_input.send_keys(message)
                motd_input.send_keys("\n")
                return True
        return False

    def invite_member(self, player_name: str) -> bool:
        """
        Invite player to guild

        Args:
            player_name (str): Player name to invite

        Returns:
            bool: True if invite sent
        """
        invite_button = self._element.find_element(by="type", value="invite_button")
        if invite_button:
            invite_button.click()
            name_input = self._element.find_element(by="type", value="player_name")
            if name_input:
                name_input.send_keys(player_name)
                name_input.send_keys("\n")
                return True
        return False

    def search_members(self, query: str) -> List[GuildMember]:
        """
        Search members by name or note

        Args:
            query (str): Search query

        Returns:
            List[GuildMember]: List of matching members
        """
        search_box = self._element.find_element(by="type", value="search")
        if search_box:
            search_box.send_keys(query)

        results = self._element.find_elements(by="type", value="search_result")
        return [GuildMember(r, self._session) for r in results]

    def get_online_members(self) -> List[GuildMember]:
        """
        Get all online members

        Returns:
            List[GuildMember]: List of online members
        """
        return [m for m in self.get_members() if m.is_online]

    def wait_for_member_online(self, name: str, timeout: float = 10) -> bool:
        """
        Wait for member to come online

        Args:
            name (str): Member name
            timeout (float): Maximum wait time in seconds

        Returns:
            bool: True if member came online within timeout
        """
        return self._session.wait_for_condition(
            lambda: self.get_member(name) and self.get_member(name).is_online,
            timeout=timeout,
            error_message=f"Member '{name}' did not come online"
        )

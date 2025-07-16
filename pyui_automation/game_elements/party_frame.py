from typing import Optional, Any, Dict, List, Tuple, TYPE_CHECKING
from ..elements.base import UIElement

if TYPE_CHECKING:
    from ..core.session import AutomationSession


class PartyMember(UIElement):
    """Represents a party/raid member frame"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def name(self) -> str:
        """Get member name"""
        return self._element.get_property("name")

    @property
    def class_name(self) -> str:
        """Get member class"""
        return self._element.get_property("class")

    @property
    def role(self) -> str:
        """Get member role (tank/healer/dps)"""
        return self._element.get_property("role")

    @property
    def level(self) -> int:
        """Get member level"""
        return self._element.get_property("level")

    @property
    def health(self) -> Tuple[int, int]:
        """Get current and maximum health"""
        return (
            self._element.get_property("current_health"),
            self._element.get_property("max_health")
        )

    @property
    def resource(self) -> Tuple[int, int]:
        """Get current and maximum resource (mana/energy/rage)"""
        return (
            self._element.get_property("current_resource"),
            self._element.get_property("max_resource")
        )

    @property
    def is_online(self) -> bool:
        """Check if member is online"""
        return self._element.get_property("online")

    @property
    def is_dead(self) -> bool:
        """Check if member is dead"""
        return self._element.get_property("dead")

    @property
    def is_leader(self) -> bool:
        """Check if member is party/raid leader"""
        return self._element.get_property("leader")

    @property
    def buffs(self) -> List[Dict[str, Any]]:
        """Get member buffs"""
        return self._element.get_property("buffs") or []

    @property
    def debuffs(self) -> List[Dict[str, Any]]:
        """Get member debuffs"""
        return self._element.get_property("debuffs") or []

    def target(self) -> bool:
        """
        Target this member

        Returns:
            bool: True if successful
        """
        self._element.click()
        return True

    def promote_leader(self) -> bool:
        """
        Promote member to leader

        Returns:
            bool: True if successful
        """
        if not self.is_leader:
            promote_button = self._element.find_element(by="type", value="promote_leader")
            if promote_button and promote_button.is_enabled():
                promote_button.click()
                return True
        return False

    def kick(self) -> bool:
        """
        Kick member from group

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

    def set_role(self, role: str) -> bool:
        """
        Set member role

        Args:
            role (str): New role (tank/healer/dps)

        Returns:
            bool: True if successful
        """
        role_button = self._element.find_element(by="type", value="role_button")
        if role_button:
            role_button.click()
            role_option = self._element.find_element(by="type", value="role_option", role=role)
            if role_option:
                role_option.click()
                return True
        return False

    def wait_until_alive(self, timeout: float = 10) -> bool:
        """
        Wait until member is alive

        Args:
            timeout (float): Maximum wait time in seconds

        Returns:
            bool: True if alive within timeout
        """
        return self._session.wait_for_condition(
            lambda: not self.is_dead,
            timeout=timeout,
            error_message=f"Member '{self.name}' did not resurrect"
        )

    def wait_for_buff(self, buff_name: str, timeout: float = 10) -> bool:
        """
        Wait for specific buff to appear

        Args:
            buff_name (str): Buff name to wait for
            timeout (float): Maximum wait time in seconds

        Returns:
            bool: True if buff appears within timeout
        """
        return self._session.wait_for_condition(
            lambda: any(b["name"] == buff_name for b in self.buffs),
            timeout=timeout,
            error_message=f"Buff '{buff_name}' did not appear"
        )


class PartyFrame(UIElement):
    """Represents the party/raid interface"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def is_raid(self) -> bool:
        """Check if group is raid"""
        return self._element.get_property("is_raid")

    @property
    def size(self) -> int:
        """Get group size"""
        return len(self.get_members())

    @property
    def leader(self) -> Optional[PartyMember]:
        """Get party/raid leader"""
        for member in self.get_members():
            if member.is_leader:
                return member
        return None

    def get_members(self, role: Optional[str] = None) -> List[PartyMember]:
        """
        Get group members, optionally filtered by role

        Args:
            role (Optional[str]): Filter by role (tank/healer/dps)

        Returns:
            List[PartyMember]: List of members
        """
        members = self._element.find_elements(
            by="type",
            value="party_member",
            role=role
        )
        return [PartyMember(m, self._session) for m in members]

    def get_member(self, name: str) -> Optional[PartyMember]:
        """
        Find member by name

        Args:
            name (str): Member name

        Returns:
            Optional[PartyMember]: Found member or None
        """
        members = self._element.find_elements(
            by="type",
            value="member",
            name=name
        )
        if not members:
            return None
        return PartyMember(members[0], self._session)

    def convert_to_raid(self) -> bool:
        """
        Convert party to raid

        Returns:
            bool: True if successful
        """
        if not self.is_raid:
            convert_button = self._element.find_element(by="type", value="convert_raid")
            if convert_button and convert_button.is_enabled():
                convert_button.click()
                return True
        return False

    def convert_to_party(self) -> bool:
        """
        Convert raid to party

        Returns:
            bool: True if successful
        """
        if self.is_raid:
            convert_button = self._element.find_element(by="type", value="convert_party")
            if convert_button and convert_button.is_enabled():
                convert_button.click()
                return True
        return False

    def invite_player(self, player_name: str) -> bool:
        """
        Invite player to group

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

    def ready_check(self) -> bool:
        """
        Initiate ready check

        Returns:
            bool: True if check started
        """
        check_button = self._element.find_element(by="type", value="ready_check")
        if check_button and check_button.is_enabled():
            check_button.click()
            return True
        return False

    def get_dead_members(self) -> List[PartyMember]:
        """
        Get all dead members

        Returns:
            List[PartyMember]: List of dead members
        """
        return [m for m in self.get_members() if m.is_dead]

    def get_offline_members(self) -> List[PartyMember]:
        """
        Get all offline members

        Returns:
            List[PartyMember]: List of offline members
        """
        return [m for m in self.get_members() if not m.is_online]

    def wait_for_size(self, size: int, timeout: float = 10) -> bool:
        """
        Wait until group reaches specific size

        Args:
            size (int): Target size
            timeout (float): Maximum wait time in seconds

        Returns:
            bool: True if size reached within timeout
        """
        return self._session.wait_for_condition(
            lambda: self.size == size,
            timeout=timeout,
            error_message=f"Group did not reach size {size}"
        )

    def wait_all_alive(self, timeout: float = 10) -> bool:
        """
        Wait until all members are alive

        Args:
            timeout (float): Maximum wait time in seconds

        Returns:
            bool: True if all alive within timeout
        """
        return self._session.wait_for_condition(
            lambda: len(self.get_dead_members()) == 0,
            timeout=timeout,
            error_message="Not all members are alive"
        )

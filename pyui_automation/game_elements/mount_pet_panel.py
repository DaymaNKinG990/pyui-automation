from typing import Optional, Any, Dict, List, Tuple
from ..elements.base import UIElement


class Mount(UIElement):
    """Represents a mount in the collection"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def name(self) -> str:
        """Get mount name"""
        return self._element.get_property("name")

    @property
    def type(self) -> str:
        """Get mount type (ground/flying/water)"""
        return self._element.get_property("type")

    @property
    def speed(self) -> int:
        """Get mount speed bonus"""
        return self._element.get_property("speed")

    @property
    def is_favorite(self) -> bool:
        """Check if mount is favorited"""
        return self._element.get_property("favorite")

    @property
    def is_active(self) -> bool:
        """Check if mount is currently summoned"""
        return self._element.get_property("active")

    @property
    def is_unlocked(self) -> bool:
        """Check if mount is unlocked"""
        return self._element.get_property("unlocked")

    def summon(self) -> bool:
        """
        Summon this mount

        Returns:
            bool: True if successful
        """
        if not self.is_unlocked or self.is_active:
            return False

        self._element.click()
        summon_button = self._element.find_element(by="type", value="summon_button")
        if summon_button and summon_button.is_enabled():
            summon_button.click()
            return True
        return False

    def set_favorite(self, favorite: bool = True) -> bool:
        """
        Set mount favorite status

        Args:
            favorite (bool): New favorite status

        Returns:
            bool: True if successful
        """
        if self.is_favorite != favorite:
            favorite_button = self._element.find_element(by="type", value="favorite_button")
            if favorite_button:
                favorite_button.click()
                return True
        return False


class Pet(UIElement):
    """Represents a pet in the collection"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def name(self) -> str:
        """Get pet name"""
        return self._element.get_property("name")

    @property
    def type(self) -> str:
        """Get pet type/family"""
        return self._element.get_property("type")

    @property
    def level(self) -> int:
        """Get pet level"""
        return self._element.get_property("level")

    @property
    def happiness(self) -> int:
        """Get pet happiness level"""
        return self._element.get_property("happiness")

    @property
    def is_favorite(self) -> bool:
        """Check if pet is favorited"""
        return self._element.get_property("favorite")

    @property
    def is_active(self) -> bool:
        """Check if pet is currently summoned"""
        return self._element.get_property("active")

    @property
    def abilities(self) -> List[str]:
        """Get pet abilities"""
        return self._element.get_property("abilities") or []

    def summon(self) -> bool:
        """
        Summon this pet

        Returns:
            bool: True if successful
        """
        if self.is_active:
            return False

        self._element.click()
        summon_button = self._element.find_element(by="type", value="summon_button")
        if summon_button and summon_button.is_enabled():
            summon_button.click()
            return True
        return False

    def dismiss(self) -> bool:
        """
        Dismiss this pet

        Returns:
            bool: True if successful
        """
        if not self.is_active:
            return False

        dismiss_button = self._element.find_element(by="type", value="dismiss_button")
        if dismiss_button and dismiss_button.is_enabled():
            dismiss_button.click()
            return True
        return False

    def rename(self, new_name: str) -> bool:
        """
        Rename the pet

        Args:
            new_name (str): New pet name

        Returns:
            bool: True if successful
        """
        rename_button = self._element.find_element(by="type", value="rename_button")
        if rename_button:
            rename_button.click()
            name_input = self._element.find_element(by="type", value="name_input")
            if name_input:
                name_input.send_keys(new_name)
                name_input.send_keys("\n")
                return True
        return False

    def set_favorite(self, favorite: bool = True) -> bool:
        """
        Set pet favorite status

        Args:
            favorite (bool): New favorite status

        Returns:
            bool: True if successful
        """
        if self.is_favorite != favorite:
            favorite_button = self._element.find_element(by="type", value="favorite_button")
            if favorite_button:
                favorite_button.click()
                return True
        return False


class MountPetPanel(UIElement):
    """Represents the mount and pet collection interface"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def active_mount(self) -> Optional[Mount]:
        """Get currently active mount"""
        mount = self._element.find_element(
            by="type",
            value="mount",
            active=True
        )
        return Mount(mount, self._session) if mount else None

    @property
    def active_pet(self) -> Optional[Pet]:
        """Get currently active pet"""
        pet = self._element.find_element(
            by="type",
            value="pet",
            active=True
        )
        return Pet(pet, self._session) if pet else None

    def get_mounts(self, mount_type: Optional[str] = None) -> List[Mount]:
        """
        Get mount collection, optionally filtered by type

        Args:
            mount_type (Optional[str]): Filter by mount type

        Returns:
            List[Mount]: List of mounts
        """
        mounts = self._element.find_elements(
            by="type",
            value="mount",
            mount_type=mount_type
        )
        return [Mount(m, self._session) for m in mounts]

    def get_pets(self, pet_type: Optional[str] = None) -> List[Pet]:
        """
        Get pet collection, optionally filtered by type

        Args:
            pet_type (Optional[str]): Filter by pet type

        Returns:
            List[Pet]: List of pets
        """
        pets = self._element.find_elements(
            by="type",
            value="pet",
            pet_type=pet_type
        )
        return [Pet(p, self._session) for p in pets]

    def get_mount(self, name: str) -> Optional[Mount]:
        """
        Find mount by name

        Args:
            name (str): Mount name

        Returns:
            Optional[Mount]: Found mount or None
        """
        mount = self._element.find_element(
            by="type",
            value="mount",
            name=name
        )
        return Mount(mount, self._session) if mount else None

    def get_pet(self, name: str) -> Optional[Pet]:
        """
        Find pet by name

        Args:
            name (str): Pet name

        Returns:
            Optional[Pet]: Found pet or None
        """
        pet = self._element.find_element(
            by="type",
            value="pet",
            name=name
        )
        return Pet(pet, self._session) if pet else None

    def get_favorite_mounts(self) -> List[Mount]:
        """
        Get favorited mounts

        Returns:
            List[Mount]: List of favorite mounts
        """
        mounts = self._element.find_elements(
            by="type",
            value="mount",
            favorite=True
        )
        return [Mount(m, self._session) for m in mounts]

    def get_favorite_pets(self) -> List[Pet]:
        """
        Get favorited pets

        Returns:
            List[Pet]: List of favorite pets
        """
        pets = self._element.find_elements(
            by="type",
            value="pet",
            favorite=True
        )
        return [Pet(p, self._session) for p in pets]

    def summon_random_favorite(self, mount: bool = True) -> bool:
        """
        Summon random favorite mount or pet

        Args:
            mount (bool): True for mount, False for pet

        Returns:
            bool: True if successful
        """
        random_button = self._element.find_element(
            by="type",
            value="random_button",
            mount=mount
        )
        if random_button and random_button.is_enabled():
            random_button.click()
            return True
        return False

    def wait_for_mount(self, timeout: float = 10) -> bool:
        """
        Wait until a mount is summoned

        Args:
            timeout (float): Maximum wait time in seconds

        Returns:
            bool: True if mounted within timeout
        """
        return self._session.wait_for_condition(
            lambda: self.active_mount is not None,
            timeout=timeout,
            error_message="Mount was not summoned"
        )

    def wait_for_pet(self, timeout: float = 10) -> bool:
        """
        Wait until a pet is summoned

        Args:
            timeout (float): Maximum wait time in seconds

        Returns:
            bool: True if pet summoned within timeout
        """
        return self._session.wait_for_condition(
            lambda: self.active_pet is not None,
            timeout=timeout,
            error_message="Pet was not summoned"
        )

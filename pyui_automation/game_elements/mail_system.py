from typing import Optional, Any, Dict, List, Tuple
from datetime import datetime
from ..elements.base import UIElement


class MailAttachment(UIElement):
    """Represents an item attached to mail"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def name(self) -> str:
        """Get item name"""
        return self._element.get_property("name")

    @property
    def quantity(self) -> int:
        """Get item quantity"""
        return self._element.get_property("quantity")

    @property
    def can_take(self) -> bool:
        """Check if item can be taken"""
        return self._element.get_property("can_take")

    def take(self) -> bool:
        """
        Take item from mail

        Returns:
            bool: True if successful
        """
        if self.can_take:
            self._element.click()
            return True
        return False


class Mail(UIElement):
    """Represents a mail message"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def subject(self) -> str:
        """Get mail subject"""
        return self._element.get_property("subject")

    @property
    def sender(self) -> str:
        """Get sender name"""
        return self._element.get_property("sender")

    @property
    def text(self) -> str:
        """Get mail body text"""
        return self._element.get_property("text")

    @property
    def received_time(self) -> datetime:
        """Get time mail was received"""
        return self._element.get_property("received_time")

    @property
    def expires_in(self) -> int:
        """Get hours until mail expires"""
        return self._element.get_property("expires_in")

    @property
    def has_gold(self) -> bool:
        """Check if mail has gold attached"""
        return self._element.get_property("has_gold")

    @property
    def gold_amount(self) -> int:
        """Get attached gold amount"""
        return self._element.get_property("gold_amount")

    @property
    def is_read(self) -> bool:
        """Check if mail has been read"""
        return self._element.get_property("read")

    @property
    def attachments(self) -> List[MailAttachment]:
        """Get mail attachments"""
        attachments = self._element.find_elements(by="type", value="attachment")
        return [MailAttachment(a, self._session) for a in attachments]

    def take_gold(self) -> bool:
        """
        Take attached gold

        Returns:
            bool: True if successful
        """
        if self.has_gold:
            take_button = self._element.find_element(by="type", value="take_gold")
            if take_button and take_button.is_enabled():
                take_button.click()
                return True
        return False

    def take_all_attachments(self) -> bool:
        """
        Take all attachments

        Returns:
            bool: True if all items taken
        """
        take_all_button = self._element.find_element(by="type", value="take_all")
        if take_all_button and take_all_button.is_enabled():
            take_all_button.click()
            return True
        return False

    def delete(self) -> bool:
        """
        Delete the mail

        Returns:
            bool: True if successful
        """
        delete_button = self._element.find_element(by="type", value="delete_button")
        if delete_button and delete_button.is_enabled():
            delete_button.click()
            return True
        return False

    def return_to_sender(self) -> bool:
        """
        Return mail to sender

        Returns:
            bool: True if successful
        """
        return_button = self._element.find_element(by="type", value="return_button")
        if return_button and return_button.is_enabled():
            return_button.click()
            return True
        return False


class MailSystem(UIElement):
    """Represents the mail system interface"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def inbox_count(self) -> int:
        """Get number of mails in inbox"""
        return self._element.get_property("inbox_count")

    @property
    def unread_count(self) -> int:
        """Get number of unread mails"""
        return self._element.get_property("unread_count")

    def get_mail(self, index: int = 0) -> Optional[Mail]:
        """
        Get mail by index

        Args:
            index (int): Mail index in inbox

        Returns:
            Optional[Mail]: Mail message or None
        """
        mail = self._element.find_element(
            by="type",
            value="mail",
            index=index
        )
        return Mail(mail, self._session) if mail else None

    def get_all_mail(self) -> List[Mail]:
        """
        Get all mail in inbox

        Returns:
            List[Mail]: List of mail messages
        """
        mails = self._element.find_elements(by="type", value="mail")
        return [Mail(m, self._session) for m in mails]

    def get_unread_mail(self) -> List[Mail]:
        """
        Get unread mail

        Returns:
            List[Mail]: List of unread messages
        """
        mails = self._element.find_elements(
            by="type",
            value="mail",
            read=False
        )
        return [Mail(m, self._session) for m in mails]

    def send_mail(self,
                 recipient: str,
                 subject: str,
                 body: str,
                 gold: Optional[int] = None,
                 items: Optional[List[str]] = None) -> bool:
        """
        Send new mail

        Args:
            recipient (str): Recipient name
            subject (str): Mail subject
            body (str): Mail body text
            gold (Optional[int]): Gold amount to attach
            items (Optional[List[str]]): Item names to attach

        Returns:
            bool: True if mail sent successfully
        """
        compose_button = self._element.find_element(by="type", value="compose_button")
        if not compose_button or not compose_button.is_enabled():
            return False

        compose_button.click()

        # Fill recipient
        to_input = self._element.find_element(by="type", value="recipient_input")
        if to_input:
            to_input.send_keys(recipient)

        # Fill subject
        subject_input = self._element.find_element(by="type", value="subject_input")
        if subject_input:
            subject_input.send_keys(subject)

        # Fill body
        body_input = self._element.find_element(by="type", value="body_input")
        if body_input:
            body_input.send_keys(body)

        # Attach gold
        if gold is not None and gold > 0:
            gold_input = self._element.find_element(by="type", value="gold_input")
            if gold_input:
                gold_input.send_keys(str(gold))

        # Attach items
        if items:
            for item_name in items:
                # Find item in inventory
                inventory = self._element.find_elements(by="type", value="inventory_item")
                for item in inventory:
                    if item.get_property("name") == item_name:
                        item.click()
                        break

        # Send mail
        send_button = self._element.find_element(by="type", value="send_button")
        if send_button and send_button.is_enabled():
            send_button.click()
            return True

        return False

    def delete_all_read(self) -> bool:
        """
        Delete all read mail

        Returns:
            bool: True if successful
        """
        delete_read_button = self._element.find_element(by="type", value="delete_read")
        if delete_read_button and delete_read_button.is_enabled():
            delete_read_button.click()
            confirm_button = self._element.find_element(by="type", value="confirm_delete")
            if confirm_button:
                confirm_button.click()
                return True
        return False

    def take_all_attachments(self) -> bool:
        """
        Take all attachments from all mail

        Returns:
            bool: True if successful
        """
        take_all_button = self._element.find_element(by="type", value="take_all_button")
        if take_all_button and take_all_button.is_enabled():
            take_all_button.click()
            return True
        return False

    def wait_for_mail(self, sender: str, timeout: float = 10) -> bool:
        """
        Wait for mail from specific sender

        Args:
            sender (str): Sender name
            timeout (float): Maximum wait time in seconds

        Returns:
            bool: True if mail received within timeout
        """
        def check_mail():
            for mail in self.get_all_mail():
                if mail.sender == sender:
                    return True
            return False

        return self._session.wait_for_condition(
            check_mail,
            timeout=timeout,
            error_message=f"Mail from '{sender}' not received"
        )

    def wait_until_empty(self, timeout: float = 10) -> bool:
        """
        Wait until inbox is empty

        Args:
            timeout (float): Maximum wait time in seconds

        Returns:
            bool: True if inbox empty within timeout
        """
        return self._session.wait_for_condition(
            lambda: self.inbox_count == 0,
            timeout=timeout,
            error_message="Inbox not empty"
        )

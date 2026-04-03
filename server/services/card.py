"""
Service for managing Trello cards in MCP server.
"""

from typing import Any, Dict, List

from server.models import TrelloAttachment, TrelloCard
from server.utils.trello_api import TrelloClient


class CardService:
    """
    Service class for managing Trello cards.
    """

    def __init__(self, client: TrelloClient):
        self.client = client

    async def get_card(self, card_id: str) -> TrelloCard:
        """Retrieves a specific card by its ID.

        Args:
            card_id (str): The ID of the card to retrieve.

        Returns:
            TrelloCard: The card object containing card details.
        """
        response = await self.client.GET(f"/cards/{card_id}")
        return TrelloCard(**response)

    async def get_cards(self, list_id: str) -> List[TrelloCard]:
        """Retrieves all cards in a given list.

        Args:
            list_id (str): The ID of the list whose cards to retrieve.

        Returns:
            List[TrelloCard]: A list of card objects.
        """
        response = await self.client.GET(f"/lists/{list_id}/cards")
        return [TrelloCard(**card) for card in response]

    async def create_card(self, **kwargs) -> TrelloCard:
        """Creates a new card in a given list.

        Args
            list_id (str): The ID of the list to create the card in.
            name (str): The name of the new card.
            desc (str, optional): The description of the new card. Defaults to None.

        Returns:
            TrelloCard: The newly created card object.
        """
        response = await self.client.POST("/cards", data=kwargs)
        return TrelloCard(**response)

    async def update_card(self, card_id: str, **kwargs) -> TrelloCard:
        """Updates a card's attributes.

        Args:
            card_id (str): The ID of the card to update.
            **kwargs: Keyword arguments representing the attributes to update on the card.

        Returns:
            TrelloCard: The updated card object.
        """
        response = await self.client.PUT(f"/cards/{card_id}", data=kwargs)
        return TrelloCard(**response)

    async def delete_card(self, card_id: str) -> Dict[str, Any]:
        """Deletes a card.

        Args:
            card_id (str): The ID of the card to delete.

        Returns:
            Dict[str, Any]: The response from the delete operation.
        """
        return await self.client.DELETE(f"/cards/{card_id}")

    async def get_card_attachments(self, card_id: str) -> List[TrelloAttachment]:
        response = await self.client.GET(f"/cards/{card_id}/attachments")
        return [TrelloAttachment(**attachment) for attachment in response]

    async def get_card_attachment_image(self, card_id: str, attachment_id: str) -> tuple[bytes, str]:
        response = await self.client.GET(f"/cards/{card_id}/attachments/{attachment_id}")
        attachment = TrelloAttachment(**response)

        if not attachment.mimeType or not attachment.mimeType.startswith("image/"):
            raise ValueError(f"Attachment '{attachment.name}' is not an image (type: {attachment.mimeType})")

        # Trello returns download URLs on trello.com, but auth works on api.trello.com
        download_url = attachment.url.replace("https://trello.com/1/", "https://api.trello.com/1/")
        image_bytes = await self.client.GET_bytes_url(download_url)
        return image_bytes, attachment.mimeType

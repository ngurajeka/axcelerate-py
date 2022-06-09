import datetime

from axcelerate.client import Client
from axcelerate.exceptions import ContactNotFoundException, CreateContactFailedException, CreateContactNoteFailedException, \
    CreateContactPortfolioFailedException
from axcelerate.file import File
from pydantic import BaseModel, Field
from typing import List, Optional


class Contact(object):
    id: int = None
    given_name: str = ''
    surname: str = ''
    email_address: str = ''
    mobile_phone: str = ''
    categories: list = []
    contact_active: bool = True
    dob: datetime.date = None
    address1: str = None
    address2: str = None
    country: str = None
    source_code_id: int = None
    custom_fields = {}


class ContactNote(BaseModel):
    id : int = Field(..., alias='ID'),
    row_id : int = Field(..., alias='ROWID'),
    text : str = Field(..., alias='TEXT')
    contact_type : str = Field(..., alias='TYPE')
    created_at : datetime.datetime = Field(..., alias='DATEINSERTED')
    created_by : str = Field(..., alias='ADDEDBY')
    created_by_id : int = Field(..., alias='ADDEDBYCONTACTID')
    updated_at : Optional[datetime.datetime] = Field(..., alias='DATEUPDATED')
    updated_by : Optional[str] = Field(..., alias='UPDATEDBY') 
    updated_by_id : Optional[int] = Field(..., alias='UPDATEDBYCONTACTID')
    attachment : Optional[str] = Field(..., alias='ATTACHMENT')
    count : int = Field(..., alias='COUNT')


class ContactAPI(Client):

    def _build_response(self, json_response):
        contact = Contact()
        contact.id = json_response.get('CONTACTID')
        contact.given_name = json_response.get('GIVENNAME')
        contact.surname = json_response.get('SURNAME')
        contact.email_address = json_response.get('EMAILADDRESS')
        contact.mobile_phone = json_response.get('MOBILEPHONE')
        contact.categories = json_response.get('CATEGORYIDS', [])
        contact.source_code_id = json_response.get('SOURCECODEID', None)
        contact.contact_active = json_response.get('CONTACTACTIVE', True)
        contact.dob = json_response.get('DOB', None)
        contact.country = json_response.get('COUNTRY', None)
        contact.address1 = json_response.get('ADDRESS1', None)
        contact.address2 = json_response.get('ADDRESS2', None)
        return contact

    def get_contact(self, contact_id) -> Contact:
        response = self.get('contact/%d' % contact_id)
        if response.status_code != 200:
            raise ContactNotFoundException()

        json_response = response.json()
        return self._build_response(json_response)

    def search_contact(self, params) -> list:
        response = self.get('contacts/search', params=params)
        if response.status_code != 200:
            return []
        responses = response.json()
        contacts = []
        for json_response in responses:
            contacts.append(self._build_response(json_response))
        return contacts

    def add_contact(self, contact: Contact) -> int:
        payload = {
            'givenName': contact.given_name,
            'surname': contact.surname,
            'emailAddress': contact.email_address,
            'mobilephone': contact.mobile_phone,
            'categoryIDs': contact.categories,
            'SourceCodeID': contact.source_code_id,
            'ContactActive': contact.contact_active,
            'dob': contact.dob,
            'country': contact.country,
            'address1': contact.address1,
            'address2': contact.address2,
        }

        for field, value in contact.custom_fields.items():
            key = 'customField_%s' % field
            payload[key] = value

        response = self.post('contact', payload)
        json_response = response.json()
        if response.status_code != 200:
            raise CreateContactFailedException(json_response.get('DETAILS'))

        return int(json_response.get('CONTACTID'))

    def add_contact_notes(self, contact_id, note) -> int:
        payload = {
            'contactID': contact_id,
            'contactNote': note,
        }
        response = self.post('contact/note', payload)
        json_response = response.json()
        if response.status_code != 200:
            raise CreateContactNoteFailedException(json_response.get('MESSAGES'))

        return int(json_response.get('NOTEID'))

    def search_contact_notes(self, contact_id, q=None) -> List[ContactNote]:
        params = {'search': q}
        response = self.get(f'contact/notes/{contact_id}', params=params)
        if response.status_code != 200:
            return []

        contact_notes = []
        for json_response in response.json():
            contact_notes.append(ContactNote(**json_response))
        return contact_notes

    def add_portfolio(self, contact_id, portfolio_type: int):
        payload = {
            'contactID': contact_id,
            'portfolioTypeID': portfolio_type,
        }
        response = self.post('contact/portfolio', payload)
        json_response = response.json()
        if response.status_code != 200:
            raise CreateContactPortfolioFailedException(json_response.get('MESSAGES'))

        return int(json_response.get('PORTFOLIOID'))

    def add_portfolio_file(self, contact_id: int, portfolio_id: int, portfolio: File):
        payload = {
            'contactID': contact_id,
            'portfolioID': portfolio_id,
        }
        response = self.upload('contact/portfolio/file', payload, portfolio)
        json_response = response.json()
        if response.status_code != 200:
            raise CreateContactPortfolioFailedException(json_response.get('MESSAGES'))

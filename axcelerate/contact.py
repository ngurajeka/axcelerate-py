import datetime
import re

from axcelerate.client import Client
from axcelerate.exceptions import ContactNotFoundException, ContactPortfolioNotFoundException, CreateContactFailedException, CreateContactNoteFailedException, \
    CreateContactPortfolioFailedException
from axcelerate.file import File
from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class Contact(BaseModel):
    id: Optional[int] = Field(alias='CONTACTID', default=None)
    given_name: str = Field(alias='GIVENNAME')
    surname: str = Field(alias='SURNAME')
    email_address: str = Field(alias='EMAILADDRESS')
    mobile_phone: Optional[str] = Field(alias='MOBILEPHONE', default=None)
    categories: List[int] = Field(alias='CATEGORYIDS', default=[])
    contact_active: bool = Field(alias='CONTACTACTIVE', default=True)
    dob: Optional[datetime.date] = Field(alias='DOB', default=None)
    address1: Optional[str] = Field(alias='ADDRESS1', default=None)
    address2: Optional[str] = Field(alias='ADDRESS2', default=None)
    country: Optional[str] = Field(alias='COUNTRY', default=None)
    source_code_id: Optional[int] = Field(alias='SOURCECODEID', default=None)
    custom_fields: Dict = {}

    class Config:
        allow_population_by_field_name = True

    def generate_payload(self):
        payload = self.dict(by_alias=True, exclude={'contact_active', 'custom_fields'})

        for field in self.custom_fields:
            value = self.custom_fields.get(field)
            payload[f'customField_{field}'.upper()] = value

        return payload

    @staticmethod
    def build(json_data: dict):
        custom_fields = [key for key in json_data.keys() if re.match('CUSTOMFIELD_+', key)]
        custom_fields_data = {}
        for key in custom_fields:
            custom_fields_data[key[12:]] = json_data.pop(key)
        contact = Contact.parse_obj(json_data)
        contact.custom_fields = custom_fields_data
        return contact


class ContactNote(BaseModel):
    id: int = Field(..., alias='NOTEID'),
    row_id: int = Field(..., alias='ROWID'),
    text: str = Field(..., alias='TEXT')
    contact_type: str = Field(..., alias='TYPE')
    created_at: datetime.datetime = Field(..., alias='DATEINSERTED')
    created_by: str = Field(..., alias='ADDEDBY')
    created_by_id: int = Field(..., alias='ADDEDBYCONTACTID')
    updated_at: Optional[datetime.datetime] = Field(..., alias='DATEUPDATED')
    updated_by: Optional[str] = Field(..., alias='UPDATEDBY') 
    updated_by_id: Optional[int] = Field(..., alias='UPDATEDBYCONTACTID')
    attachment: Optional[str] = Field(..., alias='ATTACHMENT')
    count: int = Field(..., alias='COUNT')


class ContactAPI(Client):

    def get_contact(self, contact_id) -> Contact:
        response = self.get('contact/%d' % contact_id)
        if response.status_code != 200:
            raise ContactNotFoundException()

        json_response = response.json()
        return Contact.build(json_response)

    def search_contact(self, params) -> List[Contact]:
        response = self.get('contacts/search', params=params)
        if response.status_code != 200:
            return []
        responses = response.json()
        contacts = list(map(lambda x: Contact.build(x), responses))
        return contacts

    def add_contact(self, contact: Contact) -> int:
        response = self.post('contact', contact.generate_payload())
        json_response = response.json()
        if response.status_code != 200:
            raise CreateContactFailedException(json_response.get('DETAILS'))

        return Contact.build(json_response).id

    def update_contact(self, contact: Contact, custom_fields: List[str] = []) -> Contact:
        response = self.put(f'contact/{contact.id}', contact.generate_payload(custom_fields))
        json_response = response.json()
        if response.status_code != 200:
            raise CreateContactFailedException(json_response.get('DETAILS'))

        return Contact.build(json_response)

    def add_contact_notes(self, contact_id, note) -> int:
        payload = {
            'contactID': contact_id,
            'contactNote': note,
        }
        response = self.post('contact/note', payload)
        json_response = response.json()
        if response.status_code != 200:
            raise CreateContactNoteFailedException(json_response.get('MESSAGES'))

        return ContactNote(**json_response).id

    def search_contact_notes(self, contact_id, q=None) -> List[ContactNote]:
        params = {'search': q}
        response = self.get(f'contact/notes/{contact_id}', params=params)
        if response.status_code != 200:
            return []

        return list(map(lambda x: ContactNote(**x), response.json()))

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

    def get_portfolio(self, contact_id, portfolio_type: int):
        params = {
            'contactID': contact_id,
            'portfolioTypeID': portfolio_type,
        }
        response = self.get('contact/portfolio', params)
        json_response = response.json()
        if response.status_code != 200:
            raise ContactPortfolioNotFoundException(json_response.get('MESSAGES'))

        if len(json_response) == 0:
            raise ContactPortfolioNotFoundException()

        return int(json_response[0].get('PORTFOLIOID'))

    def add_portfolio_file(self, contact_id: int, portfolio_id: int, portfolio: File):
        payload = {
            'contactID': contact_id,
            'portfolioID': portfolio_id,
        }
        response = self.upload('contact/portfolio/file', payload, portfolio)
        json_response = response.json()
        if response.status_code != 200:
            raise CreateContactPortfolioFailedException(json_response.get('MESSAGES'))

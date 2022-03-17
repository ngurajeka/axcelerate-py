import datetime
from axcelerate.client import Client
from axcelerate.exceptions import CreateContactFailedException, CreateContactNoteFailedException, \
    CreateContactPortfolioFailedException
from axcelerate.file import File


class Contact(object):
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


class ContactAPI(Client):

    def get_contact(self, contact_id) -> Contact:
        response = self.get('contact/%d' % contact_id)
        json_response = response.json()
        contact = Contact()
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

    def search_contact(self, params) -> list[Contact]:
        response = self.get('contacts/search', params=params)
        responses = response.json()
        contacts = []
        for json_response in responses:
            contact = Contact()
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
            contacts.append(contact)
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
            raise CreateContactFailedException(json_response.get('MESSAGES'))

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

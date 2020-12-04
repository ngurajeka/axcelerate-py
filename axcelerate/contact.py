from axcelerate.client import Client
from axcelerate.exceptions import CreateContactFailedException, CreateContactNoteFailedException


class Contact(object):
    given_name: str = ''
    surname: str = ''
    email_address: str = ''
    mobile_phone: str = ''
    categories: list = []


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
        return contact

    def add_contact(self, contact: Contact) -> int:
        payload = {
            'givenName': contact.given_name,
            'surname': contact.surname,
            'emailAddress': contact.email_address,
            'mobilephone': contact.mobile_phone,
            'categoryIDs': contact.categories,
        }
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

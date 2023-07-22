from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import base64
from bs4 import BeautifulSoup

SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'

def fetch_emails(service):
    # Call the Gmail API to fetch INBOX
    results = service.users().messages().list(userId='me',labelIds = ['INBOX']).execute()
    messages = results.get('messages', [])
    return messages

def parse_emails(messages, service):
    if not messages:
        print("No messages found.")
    else:
        print("Message snippets:")
        commentlist = []
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            #print(msg['payload']['parts'][0]['body']['data'])

             # Get value of 'payload' from dictionary 'txt'
            payload = msg['payload']
            headers = payload['headers']
  
            # Look for Subject and Sender Email in the headers
            for d in headers:
                if d['name'] == 'Subject':
                    subject = d['value']
                if d['name'] == 'From':
                    sender = d['value']

            if (subject.find("High Rated Tutor Session") == -1):
                continue
            # The Body of the message is in Encrypted format. So, we have to decode it.
            # Get the data and decode it with base 64 decoder.
            parts = payload.get('parts')[0]
            data = parts['body']['data']
            data = data.replace("-","+").replace("_","/")
            decoded_data = base64.b64decode(data)
  
            # Now, the data obtained is in lxml. So, we will parse 
            # it with BeautifulSoup library
            soup = BeautifulSoup(decoded_data , "lxml")
            body = soup.body()

            text = "What's great about your sessions?"
            start = str(body).find(text) 
            offset = len(text)
            end = str(body).find("What's not great about your sessions?")
            commentlist.append(str(body)[start+offset:end].strip())
  
            # Printing the subject, sender's email and message
            print("Subject: ", subject)
            print("From: ", sender)
            print("Message: ", body)
            print('\n')

    return commentlist


def main():
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))
    messages = fetch_emails(service)
    commentlist = parse_emails(messages, service)
    print(commentlist)
            

if __name__ == '__main__':
    main()     

from twilio.rest import Client
# in this part you have to replace account_sid
# auth_token, twilio_number, recipient_number with your actual credential

account_sid = 'secret'
auth_token = 'secret'
twilio_number = 'secret'
recipient_number = 'secret'

# Create Twilio client
client = Client(account_sid, auth_token)

# Send SMS
# in body part you have to write your message
message = client.messages.create(
    body='This is a test message from Twilio',
    from_=twilio_number,
    to=recipient_number
)

print("Message sent with SID: {message.sid}")
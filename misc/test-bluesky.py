from atproto import Client

client = Client()
client.login('secret', 'secret')

post = client.send_post('Hello Bluesky! I posted this via the Python SDK! Watch this space for automated postings of new images'+
                        'from my automated micro-observatory! Soon you will be able to request observations as well!')

print(f"Posted as ID: {post.uri}")
print(f"Post CID: {post.cid}")

# https://docs.bsky.app/docs/tutorials/creating-a-post
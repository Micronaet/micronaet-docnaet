# MSG
import extract_msg
import pdb

pdb.set_trace()
msg = extract_msg.openMsg('504996.msg')
msg.body()  # print(msg.dump())


# msg_raw = b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1\x00 ... \x00\x00\x00'
# msg = extract_msg.openMsg(msg_raw)
# msg = extract_msg.openMsg(
#     "path/to/msg/file.msg", attachmentClass = CustomAttachmentClass)

# EML mode 1:
# import email
message = ''  # todo
for pl in message.get_payload():
    if pl.get_content_type() in ('text/plain', 'text/html'):
        text = pl.get_payload()

# EML mode 2
'''
import email
from emaildata.metadata import MetaData

message = email.message_from_file(open('504986.eml'))
extractor = MetaData(message)
data = extractor.to_dict()
print data.keys()

# IMAP
mail_text = '\n'.join(
    [str(p.get_payload(decode=True)) for p in message.walk()])
'''


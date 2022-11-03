# Update the path below.
file = '/Users/jonahruan/.aws/credentials'

# Update keys below.
AWS_ACCESS_KEY_ID = 'AKIAR23VGBXQCKSR55YL'
AWS_SECRET_KEY = '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'


with open(file, 'w') as filetowrite:
    myCredential = f"""[default]
aws_access_key_id={AWS_ACCESS_KEY_ID}
aws_secret_access_key={AWS_SECRET_KEY}
"""
    filetowrite.write(myCredential)

# Update the path below.
file = '/Users/jonahruan/.aws/config'

with open(file, 'w') as filetowrite:
    myCredential = """[default]
                      region = us-east-1
                      output = json
                      [profile prod]
                      region = us-east-1
                      output = json"""
    filetowrite.write(myCredential)

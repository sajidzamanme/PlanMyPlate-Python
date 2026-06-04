import glob, re
import os

for f in glob.glob('app/schemas/*.py'):
    with open(f, 'r') as file:
        content = file.read()
    content = re.sub(r'\balias="([^"]+)"', r'validation_alias="\1"', content)
    with open(f, 'w') as file:
        file.write(content)
print("Updated all schemas.")

import os
from datetime import datetime

def create_metadata(image_path, meta, bucket):

    txt_path = image_path.replace(".jpg", ".txt")

    description = f"{bucket.replace('_',' ')} image showing Indian cultural context."

    content = f"""{description}

[Source: {meta['source']}]
[License: unknown-open]
[Original URL: {meta.get('url', 'N/A')}]
[Downloaded: {datetime.now().strftime('%Y-%m-%d')}]
"""

    with open(txt_path, "w") as f:
        f.write(content)
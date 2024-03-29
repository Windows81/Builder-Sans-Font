import functools
import os
import os.path
import json
import requests


@functools.cache
# C:\Users\USERNAME\AppData\Local\Roblox\Versions\version-f573c8cc796e4c97\content\fonts\
def local_font_path() -> str:
    base = os.path.join(os.getenv('LOCALAPPDATA', ''), 'Roblox', 'Versions')
    for ver in os.listdir(base):
        version_path = os.path.join(base, ver)
        fonts_path = os.path.join(version_path, 'content', 'fonts')
        if os.path.exists(fonts_path):
            return version_path
    raise FileNotFoundError()


def load_font(content_id: str) -> bytes:
    if content_id.startswith('rbxassetid://'):
        asset_id = int(content_id[13:])
        url = f'https://assetdelivery.roblox.com/v1/asset/?id={asset_id}'
        response = requests.get(url)
        if not response.ok:
            raise requests.RequestException()
        return response.content

    elif content_id.startswith('rbxasset://'):
        asset_path = content_id[11:]
        full_path = os.path.join(local_font_path(), 'content', asset_path)
        with open(full_path, 'rb') as f:
            return f.read()
    raise AttributeError()


def process_family(data) -> None:
    # Saves the family JSON file in `./families`.
    with open(os.path.join(
        'families',
        f'{data['name']}.json',
    ), 'w') as f:
        json.dump(data, f, indent='\t')

    # Loads each variant and saves to a file in `./fonts`.
    for face in data['faces']:
        font_data = load_font(face['assetId'])
        with open(os.path.join(
            'fonts',
            f'{data['name']} ({face['name']}).otf'
        ), 'wb') as f:
            f.write(font_data)


if __name__ == '__main__':
    version_path = local_font_path()
    families_path = os.path.join(version_path, 'content', 'fonts', 'families')
    for fam in os.listdir(families_path):
        fam_path = os.path.join(families_path, fam)
        with open(fam_path, 'r') as f:
            data = json.load(f)
            process_family(data)

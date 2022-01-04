#!/usr/bin/env python3

from urllib import request
from urllib.error import HTTPError
from xml.etree import ElementTree
import json
import sys
import time


RANKED_JSON = 'v2-all.json'
RANKED_TS = 'v2-all.ts'


def main():
  # kind of ghetto but probably not worth using argparse for just one parameter
  if len(sys.argv) < 2:
    print("Usage:", file=sys.stderr)
    print(f'\t{sys.argv[0]} <bsaber-username> [<count>]', file=sys.stderr)
    sys.exit(1)

  songs = set()
  titles = {}
  difficulties = None
  count = int(sys.argv[2]) if len(sys.argv) > 2 else 1

  # host doesn't like python's User-Agent
  headers = {'User-Agent': 'curl/7.74.0'}
  try:
    with open(RANKED_TS, 'r') as f:
      headers['If-Modified-Since'] = f.read()
  except FileNotFoundError:
    pass
  req = request.Request(f'https://cdn.wes.cloud/beatstar/bssb/{RANKED_JSON}',
                        headers=headers)
  print("Requesting list of ranked maps...")
  try:
    with request.urlopen(req) as response:
      body = response.read()
      with open(RANKED_JSON, 'wb') as f:
        f.write(body)
      with open(RANKED_TS, 'w') as f:
        f.write(response.headers['Last-Modified'])
  except HTTPError as e:
    if e.code != 304:
      raise

  with open(RANKED_JSON, 'r') as f:
    difficulties = json.load(f)

  url = f'https://bsaber.com/members/{sys.argv[1]}/bookmarks/feed/?acpage='
  page = 0
  while True:
    print(f"Requesting page {page + 1} of bsaber bookmarks...")
    tree = ElementTree.parse(request.urlopen(url + str(page)))
    done = True
    for item in tree.getroot().findall('channel/item'):
      done = False
      title, hash_, diffs = None, None, None
      for child in item:
        if child.tag == 'SongTitle':
          title = child.text
        if child.tag == 'Hash':
          hash_ = child.text.upper()
      try:
        diffs = [diff for diff in difficulties[hash_]['diffs']
                 if float(diff['star']) > 0]
      except KeyError:
        continue
      if len(diffs) == 0:
        continue
      for diff in diffs:
        songs.add((float(diff['star']), diff['diff'], hash_))
        titles[hash_] = title

    if done:
      break
    page += 1
    time.sleep(0.5)

  if not len(songs):
    print(f"No bookmarks found for `{sys.argv[1]}`!  Aborting.",
          file=sys.stderr)
    sys.exit(1)
  print("Generating playlist(s)...")
  songs = sorted(songs)

  songs = [{'hash': item[2], 'songName': titles[item[2]],
            'difficulties': [{'characteristic': 'Standard', 'name': item[1]}]}
           for item in songs]
  for i in range(count):
    playlist = {'playlistTitle': f'{i + 1}',
                'playlistAuthor': f'{sys.argv[1]}',
                'image': '', 'songs': songs[i::count]}
    with open(f'{i + 1}.json', 'w') as f:
      json.dump(playlist, f)
  print("Done!")


if __name__ == '__main__':
  main()

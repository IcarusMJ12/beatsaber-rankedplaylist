#!/usr/bin/env python3

from urllib import request
from xml.etree import ElementTree
import json
import sys
import time


def main():
  # kind of ghetto but probably not worth using argparse for just one parameter
  if len(sys.argv) < 2:
    print("Usage:", file=sys.stderr)
    print(f'\t{sys.argv[0]} <bsaber-username>', file=sys.stderr)
    sys.exit(1)

  songs = []

  # 'https://cdn.wes.cloud/beatstar/bssb/v2-all.json'
  difficulties = None
  with open('v2-all.json', 'r') as f:
    difficulties = json.load(f)

  url = f'https://bsaber.com/members/{sys.argv[1]}/bookmarks/feed/?acpage='
  page = 0
  while True:
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
        songs.append((float(diff['star']), diff['diff'], title, hash_))

    if done:
      break
    page += 1
    time.sleep(0.5)

  songs.sort()

  songs = [{'hash': item[3], 'songName': f'{item[0]}★ [{item[1]}] {item[2]}'}
           for item in songs]
  playlist = {'playlistTitle': 'Ranked', 'playlistAuthor': 'You',
              'image': '', 'songs': songs}
  with open('ranked.json', 'w') as f:
    json.dump(playlist, f)


if __name__ == '__main__':
  main()

# HOWTO

Requires python3.

To generate `count` playlists of alternating increasing difficulty:
`./make_ranked_playlist.py <bsaber-username> [<count>]` then copy `*.json` to
your Beat Saber playlists directory.

e.g. if your maps have difficulties `1, 2, 3, 4, 5, 6, 7` then running with
`count` of 2 will produce playlists with `1, 3, 5, 7` and `2, 4, 6`
difficulties

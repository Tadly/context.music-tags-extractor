import os
import json

import xbmc
import xbmcgui
import xbmcvfs
import xbmcaddon

import mutagen
from mutagen.easyid3 import EasyID3

_addon = xbmcaddon.Addon()

def _execute_jsonrpc(method, params=None):
    data = {}
    data['id']         = 1
    data['jsonrpc']    = '2.0'
    data['method']     = method

    if params:
        data['params'] = params

    data = json.dumps(data)
    request = xbmc.executeJSONRPC(data)

    try:
        response = json.loads(request)
    except UnicodeDecodeError:
        response = json.loads(request.decode('utf-8', 'ignore'))

    try:
        if 'result' in response:
            return response['result']
        return response
    except KeyError:
        return None

def _notify(title, message):
    xbmc.executebuiltin('Notification(%s, %s, 5000)' % (title, message))

def _translate(uid):
    return _addon.getLocalizedString(uid)

def extract_metadata(files):
    dialog = xbmcgui.Dialog()
    target_dir = dialog.browse(3, _translate(30001), 'files')
    if not target_dir:
        return

    for _file in files:
        file_path      = None
        is_remote_file = False

        if os.path.exists(_file):
            file_path = _file

        else:
            if xbmcvfs.exists(_file):
                is_remote_file = True
                file_path = os.path.join(xbmc.translatePath('special://temp'), os.path.basename(_file))

                with open(file_path, 'w+') as f:
                    f.write(xbmcvfs.File(_file).read())

        filename = os.path.basename(file_path)
        meta_filename = os.path.splitext(filename)[0] + '.meta'
        try:
            easy_tags = mutagen.File(file_path, easy=True).tags
            orig_tags = mutagen.File(file_path, easy=False).tags

            with open(os.path.join(target_dir, meta_filename), 'w+') as f:
                f.write('Mutagen EasyTags\n')
                f.write('================\n')
                for key, value in easy_tags.iteritems():
                    if isinstance(value, list):
                        for v in value:
                            f.write('%s: %s\n' % (key, v))
                    else:
                        f.write('%s: %s\n' % (key, value))

                f.write('\n\n')

                f.write('Original Tags\n')
                f.write('=============\n')
                for key, value in orig_tags.iteritems():
                    if isinstance(value, list):
                        for v in value:
                            f.write('%s: %s\n' % (key, v))
                    else:
                        f.write('%s: %s\n' % (key, value))

            _notify(_translate(30004), _translate(30005) + os.path.join(target_dir, meta_filename))

        except Exception:
            _notify(_translate(30002), _translate(30003))

        finally:
            # Remote files are copied locally so we remove them
            # again once we are finished
            if is_remote_file:
                os.remove(file_path)


# Not supported right now due to complications with mutagen
# We'd have to copy all files from a remote share which would
# take way to long for what this is supposed to do.
# Will be added in the future once I came up with a nice
# way of doing this
# =========================================================
# def _get_artist_songs(artist_id):
#     resp = _execute_jsonrpc('AudioLibrary.GetSongs', {'properties': ['artistid', 'file']})
#
#     _files = []
#     for song in resp['songs']:
#         if artist_id not in song['artistid']:
#             continue
#
#         _files.append(song['file'])
#
#     return _files
#
# def _get_album_songs(album_id):
#     resp = _execute_jsonrpc('AudioLibrary.GetSongs', {'properties': ['albumid', 'file']})
#
#     _files = []
#     for song in resp['songs']:
#         if album_id != song['albumid']:
#             continue
#
#         _files.append(song['file'])
#
#     return _files


if __name__ == '__main__':
    item_id = int(xbmc.getInfoLabel('ListItem.DBID'))
    extract_metadata([xbmc.getInfoLabel('ListItem.FileNameAndPath')])

    # Not supported right now due to complications with mutagen
    # We'd have to copy all files from a remote share which would
    # take way to long for what this is supposed to do.
    # Will be added in the future once I came up with a nice
    # way of doing this
    # =========================================================
    #
    # # We use those informations to determine what view the user is in
    # artist      = xbmc.getInfoLabel('ListItem.Artist')
    # album       = xbmc.getInfoLabel('ListItem.Album')
    # tracknumber = int(xbmc.getInfoLabel('ListItem.TrackNumber'))

    # if artist and not album and not tracknumber:
    #     # We are in the artists view
    #     extract_metadata(_get_artist_songs(item_id))

    # elif artist and album and not tracknumber:
    #     # We are in the albums view
    #     extract_metadata(_get_album_songs(item_id))

    # elif artist and album and tracknumber:
    #     # We are in the tracks view
    #     extract_metadata([xbmc.getInfoLabel('ListItem.FileNameAndPath')])

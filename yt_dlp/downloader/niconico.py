import json
import threading
import time

from .common import FileDownloader
from .external import FFmpegFD
from ..networking import Request
from ..networking.websocket import WebSocketResponse
from ..utils import DownloadError, str_or_none, truncate_string
from ..utils.traversal import traverse_obj


class NiconicoLiveFD(FileDownloader):
    """ Downloads niconico live without being stopped """

    def _parse_timeshift_position(self, position_str):
        """Parse timeshift position from hh:mm:ss format to seconds"""
        if not position_str:
            return None
        
        try:
            parts = position_str.split(':')
            if len(parts) != 3:
                raise ValueError('Invalid time format')
            
            hours, minutes, seconds = map(int, parts)
            if minutes >= 60 or seconds >= 60:
                raise ValueError('Invalid time values')
            
            return hours * 3600 + minutes * 60 + seconds
        except (ValueError, TypeError):
            self.to_screen(f'[niconico:live] Invalid timeshift position format: {position_str}. Expected hh:mm:ss')
            return None

    def real_download(self, filename, info_dict):
        video_id = info_dict['id']
        opts = info_dict['downloader_options']
        quality, ws_extractor, ws_url = opts['max_quality'], opts['ws'], opts['ws_url']
        
        # Parse timeshift position from hh:mm:ss format to seconds
        timeshift_position = self._parse_timeshift_position(self.ydl.params.get('timeshift_position'))
        
        dl = FFmpegFD(self.ydl, self.params or {})

        new_info_dict = info_dict.copy()
        new_info_dict['protocol'] = 'm3u8'

        def communicate_ws(reconnect):
            # Support --load-info-json as if it is a reconnect attempt
            if reconnect or not isinstance(ws_extractor, WebSocketResponse):
                ws = self.ydl.urlopen(Request(
                    ws_url, headers={'Origin': 'https://live.nicovideo.jp'}))
                if self.ydl.params.get('verbose', False):
                    self.write_debug('Sending startWatching request')
                ws.send(json.dumps({
                    'data': {
                        'reconnect': True,
                        'room': {
                            'commentable': True,
                            'protocol': 'webSocket',
                        },
                        'stream': {
                            'accessRightMethod': 'single_cookie',
                            'chasePlay': False,
                            'latency': 'high',
                            'protocol': 'hls',
                            'quality': quality,
                        },
                        'timeshiftPosition': timeshift_position
                    },
                    'type': 'startWatching',
                }))
            else:
                ws = ws_extractor
            with ws:
                while True:
                    recv = ws.recv()
                    if not recv:
                        continue
                    data = json.loads(recv)
                    if not data or not isinstance(data, dict):
                        continue
                    if data.get('type') == 'ping':
                        ws.send(r'{"type":"pong"}')
                        ws.send(r'{"type":"keepSeat"}')
                    elif data.get('type') == 'disconnect':
                        self.write_debug(data)
                        return True
                    elif data.get('type') == 'error':
                        self.write_debug(data)
                        message = traverse_obj(data, ('body', 'code', {str_or_none}), default=recv)
                        return DownloadError(message)
                    elif self.ydl.params.get('verbose', False):
                        self.write_debug(f'Server response: {truncate_string(recv, 100)}')

        def ws_main():
            reconnect = False
            while True:
                try:
                    ret = communicate_ws(reconnect)
                    if ret is True:
                        return
                except BaseException as e:
                    self.to_screen(
                        f'[niconico:live] {video_id}: Connection error occured, reconnecting after 10 seconds: {e}')
                    time.sleep(10)
                    continue
                finally:
                    reconnect = True

        thread = threading.Thread(target=ws_main, daemon=True)
        thread.start()

        return dl.download(filename, new_info_dict)

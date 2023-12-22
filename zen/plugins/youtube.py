from plugins.core import Field
import logging
import json

class YoutubeChannel(Field):
    
    def __init__(self, idx:int):
        super().__init__(idx)
        self.name = 'YoutubeChannel'
        self.help = 'Filters by Youtube channels. Format: channel1 channel2...'

    def process_field(self, values):
        return [value.strip().lower() for value in values]

    def is_present(self, flow):
        if 'https://www.youtube.com/youtubei/v1/player?key=' in flow.request.pretty_url:
            content = json.loads(flow.response.content)
            channel = content['videoDetails']['author']
            logging.info(channel)
            if channel and channel.lower() in self.config:
                logging.info(f'channel: {channel}')
                return True
            else: return False
        if 'https://www.youtube.com/watch?v' in flow.request.pretty_url:
            channel = self.find_soup(flow, '#watch7-content span[itemprop="author"] link[itemprop="name"]')
            if channel and channel.lower() in self.config:
                return True
            else: return False
        return True

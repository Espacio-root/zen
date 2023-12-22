from lxml import etree
import logging
import re
from bs4 import BeautifulSoup
import shlex
from config import Config, plugins


def add_placeholder_values(xml_content):
    # Match any attribute without a value
    pattern = re.compile(r'(\w+)\s*=\s*["\'][^"\']*["\']\s*')
    modified_content = pattern.sub('', xml_content)
    return modified_content

def response(flow):
    if 'https://www.youtube.com/watch?v' in flow.request.pretty_url and flow.response and flow.response.content:
        """ content = add_placeholder_values(flow.response.content.decode('utf-8')) """
        soup = BeautifulSoup(flow.response.content.decode('utf-8'), 'html.parser')
        div_elem = soup.select_one('#watch7-content span[itemprop="author"] link[itemprop="name"]')['content']
        """ span_elem = div_elem.select_one('span[itemprop="author"]') """
        logging.info(div_elem)


args = '-n -u -c youtube -f2 https://www.youtube.com/ -b wwbb'
config = Config(plugins)
config.args = args
config.run()

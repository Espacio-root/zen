from mitmproxy import ctx

def request(flow):
    print(flow.request.pretty_url)

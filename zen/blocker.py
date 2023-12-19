from mitmproxy import ctx, http
HTML_MESSAGE = "<h1>Website blocked by Zen! "

def request(flow):
    flow.response = http.Response.make(
        200,
        HTML_MESSAGE.encode(),
        {"Content-Type": "text/html"}
    )

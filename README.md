# Simple lightweight web API framework

### Usage example
```python
from whoopapi import Application, HttpRequest, HttpResponse, WebsocketHandler
import json

class WsHandler(WebsocketHandler):
    def on_message(self, message: bytes):
        response = json.dumps(
            {
                "received": message.decode(),
                "responding": f"Random response to {str(message)}",
            }
        )
        self.send(response)

application = Application()

application.route("/", methods=["GET"])
def index(request:HttpRequest):
    response = {"message": "This is the index page."}
    
    return response


@application.route("/random",methods=["GET","POST"])
def random(request:HttpRequest):
    response = HttpResponse()
    response.set_json({"message": "This is a random page", "path":request.path})

    return response


application.route_websocket(WsHandler, "/ws")

application.listen(
    port=5000,
    on_start=lambda x: print(f"Testing server running on port {x[1]}")
)
```

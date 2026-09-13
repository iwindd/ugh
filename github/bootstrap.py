import base64


class Bootstrap:
    """Initialize an empty GitHub repository through the Contents API."""

    def __init__(self, client): self.client = client

    def initialize_branch(self, branch):
        self.client.request("PUT", "/contents/.gitkeep", {"message": "chore: initialize repository", "content": base64.b64encode(b"").decode()})
        return self.client.git_data.ref(branch)

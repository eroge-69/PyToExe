def response(flow):
    if "player_auth_input" in flow.request.url:
        flow.request.content = flow.request.content.replace(
            b"InputMode::Mouse", 
            b"InputMode::Touch"
        )
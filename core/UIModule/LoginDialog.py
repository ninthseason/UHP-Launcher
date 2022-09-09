# 登录界面
from prompt_toolkit.layout import HSplit, VSplit, WindowAlign, VerticalAlign, HorizontalAlign, ConditionalContainer
from prompt_toolkit.widgets import Frame, Label, Button, TextArea

login_url = "https://login.live.com/oauth20_authorize.srf?client_id=00000000402b5328&response_type=code&scope=service%3A" \
            "%3Auser.auth.xboxlive.com%3A%3AMBI_SSL&redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf\n\n"


class LoginDialog:
    def __init__(self):
        self.textarea = TextArea(multiline=False, style="class:login-textarea")
        self.ok_btn = Button("OK")
        self.cancel_btn = Button("Cancel")
        self.dialog = ConditionalContainer(Frame(body=VSplit([HSplit(
            [
                Label(login_url),
                Label("Enter Your Access Code", align=WindowAlign.CENTER),
                self.textarea,
                VSplit(
                    [
                        self.ok_btn,
                        self.cancel_btn
                    ], align=HorizontalAlign.CENTER),
            ], width=70, align=VerticalAlign.CENTER)], align=HorizontalAlign.CENTER), title="Microsoft Login", style="class:login-frame"), False
        )

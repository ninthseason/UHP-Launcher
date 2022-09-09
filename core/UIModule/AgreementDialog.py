# 用于显示使用协议的对话框
from prompt_toolkit.shortcuts import button_dialog

agreements = """
使用须知:
--目前的使用须知仅用于开发阶段，不代表最终版本--
1. 
2. 
3. 
"""
basic_agreement = button_dialog("uhp-launcher", text=agreements, buttons=[("OK", True), ("NoRemind", False)])

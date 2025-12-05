import os
import zipfile
import shutil
from urllib.parse import urlparse

import uuid

def create_proxy_auth_extension(proxy_url, plugin_path=None):
    """
    创建一个Chrome插件来处理代理认证和SOCKS5代理
    :param proxy_url: 代理URL (e.g., socks5://user:pass@host:port)
    :param plugin_path: 插件保存路径，如果为None则在当前目录下生成
    :return: 插件目录路径
    """
    parsed = urlparse(proxy_url)
    scheme = parsed.scheme
    host = parsed.hostname
    port = parsed.port
    username = parsed.username
    password = parsed.password

    if not plugin_path:
        plugin_path = os.path.join(os.getcwd(), f"proxy_auth_plugin_{uuid.uuid4()}")

    if os.path.exists(plugin_path):
        try:
            shutil.rmtree(plugin_path)
        except Exception:
            pass
            
    try:
        os.makedirs(plugin_path, exist_ok=True)
    except FileExistsError:
        pass

    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 3,
        "name": "Proxy Auth Extension",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "service_worker": "background.js"
        },
        "minimum_chrome_version": "22.0.0"
    }
    """

    background_js = f"""
    var config = {{
        mode: "fixed_servers",
        rules: {{
            singleProxy: {{
                scheme: "{scheme}",
                host: "{host}",
                port: parseInt({port})
            }},
            bypassList: ["foobar.com"]
        }}
    }};

    chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

    function callbackFn(details) {{
        return {{
            authCredentials: {{
                username: "{username}",
                password: "{password}"
            }}
        }};
    }}

    chrome.webRequest.onAuthRequired.addListener(
        callbackFn,
        {{urls: ["<all_urls>"]}},
        ['blocking']
    );
    """

    with open(os.path.join(plugin_path, "manifest.json"), "w") as f:
        f.write(manifest_json)

    with open(os.path.join(plugin_path, "background.js"), "w") as f:
        f.write(background_js)

    return plugin_path

#!/usr/bin/env python3
"""Small local reverse proxy for Odoo worker mode.

It keeps the browser entrypoint on 127.0.0.1:8069 while routing ordinary HTTP
traffic to Odoo's prefork HTTP port and websocket traffic to the evented port.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import signal


BRAND_CN = "绿色供应链公共服务平台"
BRAND_EN = "GlobalCloud GPC"


ERROR_MESSAGES = {
    "odoo.exceptions.AccessDenied": "访问被拒绝：用户名或密码不正确，或当前账号无权访问。请检查登录信息后重试。",
    "odoo.http.SessionExpiredException": "会话已过期：请刷新页面后重新登录。",
    "werkzeug.exceptions.NotFound": "请求的接口不存在：请检查页面地址或操作是否有效。",
}


async def pipe(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    try:
        while data := await reader.read(65536):
            writer.write(data)
            await writer.drain()
    except (ConnectionError, asyncio.CancelledError):
        pass
    finally:
        writer.close()


async def read_request_body(header: bytes, reader: asyncio.StreamReader) -> bytes:
    headers = header.decode("latin1", "ignore").split("\r\n")
    content_length = 0
    for line in headers[1:]:
        name, _, value = line.partition(":")
        if name.lower() == "content-length":
            try:
                content_length = int(value.strip())
            except ValueError:
                content_length = 0
            break
    return await reader.readexactly(content_length) if content_length > 0 else b""


def localize_json_error(body: bytes) -> bytes:
    try:
        payload = json.loads(body.decode("utf-8"))
    except Exception:
        return body

    error = payload.get("error") if isinstance(payload, dict) else None
    data = error.get("data") if isinstance(error, dict) else None
    name = data.get("name") if isinstance(data, dict) else None
    message = ERROR_MESSAGES.get(name)
    if not message:
        original = (data or {}).get("message") or error.get("message", "")
        if "Session expired" in original:
            message = ERROR_MESSAGES["odoo.http.SessionExpiredException"]
        elif "Access Denied" in original:
            message = ERROR_MESSAGES["odoo.exceptions.AccessDenied"]
        elif "Not Found" in original:
            message = ERROR_MESSAGES["werkzeug.exceptions.NotFound"]

    if not message:
        return body

    error["message"] = "GlobalCloud GPC 错误提示"
    if isinstance(data, dict):
        data["message"] = message
        data["arguments"] = [message]
        data["debug"] = ""
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


def localize_html(body: bytes) -> bytes:
    try:
        text = body.decode("utf-8")
    except UnicodeDecodeError:
        return body

    replacements = {
        "Page Not Found": "页面未找到",
        "My Website": BRAND_CN,
        "@Odoo": "@GlobalCloudGPC",
        'content="Odoo"': f'content="{BRAND_EN}"',
        "Powered by Odoo": f"由 {BRAND_EN} 提供支持",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.encode("utf-8")


def transform_response(raw: bytes) -> bytes:
    if b"\r\n\r\n" not in raw:
        return raw

    header, body = raw.split(b"\r\n\r\n", 1)
    header_text = header.decode("latin1", "ignore")
    lower_header = header_text.lower()

    transformed = body
    if "content-type: application/json" in lower_header:
        transformed = localize_json_error(body)
    elif "content-type: text/html" in lower_header:
        transformed = localize_html(body)

    if transformed is body:
        return raw

    lines = header_text.split("\r\n")
    new_lines = []
    for line in lines:
        name = line.split(":", 1)[0].lower()
        if name in {"content-length", "content-encoding"}:
            continue
        new_lines.append(line)
    new_lines.append(f"Content-Length: {len(transformed)}")
    return "\r\n".join(new_lines).encode("latin1") + b"\r\n\r\n" + transformed


async def handle_client(
    client_reader: asyncio.StreamReader,
    client_writer: asyncio.StreamWriter,
    http_upstream: tuple[str, int],
    websocket_upstream: tuple[str, int],
) -> None:
    try:
        header = await client_reader.readuntil(b"\r\n\r\n")
    except (asyncio.IncompleteReadError, asyncio.LimitOverrunError):
        client_writer.close()
        return

    first_line = header.split(b"\r\n", 1)[0]
    parts = first_line.split()
    path = parts[1].decode("latin1", "ignore") if len(parts) >= 2 else "/"
    upstream = websocket_upstream if path.startswith("/websocket") else http_upstream
    request_body = b"" if path.startswith("/websocket") else await read_request_body(header, client_reader)

    try:
        upstream_reader, upstream_writer = await asyncio.open_connection(*upstream)
    except OSError:
        client_writer.write(b"HTTP/1.1 502 Bad Gateway\r\nConnection: close\r\nContent-Length: 0\r\n\r\n")
        await client_writer.drain()
        client_writer.close()
        return

    upstream_writer.write(header + request_body)
    await upstream_writer.drain()

    if path.startswith("/websocket"):
        tasks = [
            asyncio.create_task(pipe(client_reader, upstream_writer)),
            asyncio.create_task(pipe(upstream_reader, client_writer)),
        ]
        await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in tasks:
            task.cancel()
        client_writer.close()
        upstream_writer.close()
        return

    response = await upstream_reader.read()
    client_writer.write(transform_response(response))
    await client_writer.drain()
    client_writer.close()
    upstream_writer.close()


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--listen-host", default="127.0.0.1")
    parser.add_argument("--listen-port", type=int, default=8069)
    parser.add_argument("--http-host", default="127.0.0.1")
    parser.add_argument("--http-port", type=int, default=8070)
    parser.add_argument("--websocket-host", default="127.0.0.1")
    parser.add_argument("--websocket-port", type=int, default=8072)
    args = parser.parse_args()

    server = await asyncio.start_server(
        lambda reader, writer: handle_client(
            reader,
            writer,
            (args.http_host, args.http_port),
            (args.websocket_host, args.websocket_port),
        ),
        args.listen_host,
        args.listen_port,
    )

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop.set)

    async with server:
        await stop.wait()


if __name__ == "__main__":
    asyncio.run(main())

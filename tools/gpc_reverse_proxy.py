#!/usr/bin/env python3
"""Small local reverse proxy for Odoo worker mode.

It keeps the browser entrypoint on 127.0.0.1:8069 while routing ordinary HTTP
traffic to Odoo's prefork HTTP port and websocket traffic to the evented port.
"""

from __future__ import annotations

import argparse
import asyncio
import signal


async def pipe(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    try:
        while data := await reader.read(65536):
            writer.write(data)
            await writer.drain()
    except (ConnectionError, asyncio.CancelledError):
        pass
    finally:
        writer.close()


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

    try:
        upstream_reader, upstream_writer = await asyncio.open_connection(*upstream)
    except OSError:
        client_writer.write(b"HTTP/1.1 502 Bad Gateway\r\nConnection: close\r\nContent-Length: 0\r\n\r\n")
        await client_writer.drain()
        client_writer.close()
        return

    upstream_writer.write(header)
    await upstream_writer.drain()

    tasks = [
        asyncio.create_task(pipe(client_reader, upstream_writer)),
        asyncio.create_task(pipe(upstream_reader, client_writer)),
    ]
    await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    for task in tasks:
        task.cancel()
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

import aiohttp
from urllib.parse import urlsplit


class OllamaError(Exception):
    """An Ollama request failed or returned an unexpected response."""


class ImageDownloadError(Exception):
    """An attachment could not be downloaded within the configured limits."""


class OllamaClient:
    def __init__(self, session, url):
        self.session = session
        self.url = url

    async def generate(self, payload, *, timeout=300):
        try:
            async with self.session.post(
                self.url, json=payload, timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                if response.status != 200:
                    raise OllamaError(
                        f'Ollama returned HTTP {response.status}. Check the model name '
                        'and, for images, that the model supports vision.'
                    )
                data = await response.json()
        except aiohttp.ClientError as error:
            raise OllamaError('Could not connect to Ollama or read its response.') from error
        except ValueError as error:
            raise OllamaError('Ollama returned invalid JSON.') from error
        if not isinstance(data, dict) or not isinstance(data.get('response'), str):
            raise OllamaError('Ollama did not return a text response. Use its /api/generate endpoint.')
        return data['response']

    async def download_image(self, attachment, *, max_bytes):
        # Only Discord attachments are supported; message links and redirects are not fetched.
        url = urlsplit(attachment.url)
        if url.scheme != 'https' or url.hostname not in ('cdn.discordapp.com', 'media.discordapp.net'):
            raise ImageDownloadError('The attachment is not hosted on the Discord CDN.')
        try:
            async with self.session.get(
                attachment.url,
                allow_redirects=False,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                if response.status != 200:
                    raise ImageDownloadError(f'Image download returned HTTP {response.status}.')
                if response.content_length is not None and response.content_length > max_bytes:
                    raise ImageDownloadError('The image exceeds the download size limit.')
                data = bytearray()
                async for chunk in response.content.iter_chunked(64 * 1024):
                    if len(data) + len(chunk) > max_bytes:
                        raise ImageDownloadError('The image exceeds the download size limit.')
                    data.extend(chunk)
                return bytes(data)
        except aiohttp.ClientError as error:
            raise ImageDownloadError('The image could not be downloaded from Discord.') from error

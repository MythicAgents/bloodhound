import hmac
import hashlib
import base64
import requests
import datetime

from typing import Optional

DATA_START = "1970-01-01T00:00:00.000Z"
DATA_END = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z' # Now


class Credentials(object):
    def __init__(self, token_id: str, token_key: str) -> None:
        self.token_id = token_id
        self.token_key = token_key


class Client(object):
    def __init__(self, url: str, credentials: Credentials) -> None:
        self._url = url
        self._credentials = credentials

    def _format_url(self, uri: str) -> str:
        formatted_uri = uri
        if uri.startswith("/"):
            formatted_uri = formatted_uri[1:]

        return f"{self._url}/{formatted_uri}"

    def Request(self, method: str, uri: str, body: Optional[bytes] = None) -> requests.Response:
        # Digester is initialized with HMAC-SHA-256 using the token key as the HMAC digest key.
        digester = hmac.new(self._credentials.token_key.encode(), None, hashlib.sha256)

        # OperationKey is the first HMAC digest link in the signature chain. This prevents replay attacks that seek to
        # modify the request method or URI. It is composed of concatenating the request method and the request URI with
        # no delimiter and computing the HMAC digest using the token key as the digest secret.
        #
        # Example: GET /api/v1/test/resource HTTP/1.1
        # Signature Component: GET/api/v1/test/resource
        digester.update(f"{method}{uri}".encode())

        # Update the digester for further chaining
        digester = hmac.new(digester.digest(), None, hashlib.sha256)

        # DateKey is the next HMAC digest link in the signature chain. This encodes the RFC3339 formatted datetime
        # value as part of the signature to the hour to prevent replay attacks that are older than max two hours. This
        # value is added to the signature chain by cutting off all values from the RFC3339 formatted datetime from the
        # hours value forward:
        #
        # Example: 2020-12-01T23:59:60Z
        # Signature Component: 2020-12-01T23
        datetime_formatted = datetime.datetime.now().astimezone().isoformat("T")
        digester.update(datetime_formatted[:13].encode())

        # Update the digester for further chaining
        digester = hmac.new(digester.digest(), None, hashlib.sha256)

        # Body signing is the last HMAC digest link in the signature chain. This encodes the request body as part of
        # the signature to prevent replay attacks that seek to modify the payload of a signed request. In the case
        # where there is no body content the HMAC digest is computed anyway, simply with no values written to the
        # digester.
        if body is not None:
            digester.update(body)

        # Perform the request with the signed and expected headers
        return requests.request(
            method=method,
            url=self._format_url(uri),
            headers={
                "User-Agent": "bhe-python-sdk 0001",
                "Authorization": f"bhesignature {self._credentials.token_id}",
                "RequestDate": datetime_formatted,
                "Signature": base64.b64encode(digester.digest()),
                "Content-Type": "application/json",
            },
            data=body,
        )

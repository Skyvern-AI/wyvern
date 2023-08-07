# -*- coding: utf-8 -*-
from typing import Any, Dict, Union

import lz4.frame
import msgspec

msgspec_json_encoder = msgspec.json.Encoder()
msgspec_json_decoder = msgspec.json.Decoder()


def wyvern_encode(data: Dict[str, Any]) -> bytes:
    """
    encode a dict to compressed bytes using lz4.frame
    """
    return lz4.frame.compress(msgspec_json_encoder.encode(data))


def wyvern_decode(data: Union[bytes, str]) -> Dict[str, Any]:
    """
    decode compressed bytes to a dict with lz4.frame
    """
    return msgspec_json_decoder.decode(lz4.frame.decompress(data))

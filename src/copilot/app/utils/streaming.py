from anthropic.types.raw_content_block_delta_event import RawContentBlockDeltaEvent
from anthropic.types.raw_message_delta_event import RawMessageDeltaEvent
from langfuse.decorators import observe

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@observe()
def stream_tokens(stream, source_url):
    content_received = False

    for chunk in stream:
        # Check if the content is not None
        logger.info(f"----------CHUNK: {chunk} ------------")
        if (isinstance(chunk, RawContentBlockDeltaEvent)) and chunk.delta.text is not None:
            yield chunk.delta.text.encode("utf-8")
        elif (isinstance(chunk, RawMessageDeltaEvent)) and chunk.delta.stop_reason:
            yield f"\n\n<a href='{source_url}' target='_blank' class='source-link'>{source_url}</a>".encode("utf-8")
            return
        """if chunk.choices[0].delta.content is not None:
            content_received = True  # Set flag when content is processed
            yield chunk.choices[0].delta.content.encode("utf-8")

        # If the current token is None and content has been processed, it's the end of the stream
        elif chunk.choices[0].delta.content is None and content_received:
            # Send the special end token
            yield f"\n\n<a href='{source_url}' target='_blank' class='source-link'>{source_url}</a>".encode("utf-8")
            return

        # If it's a None token but no content has been processed (AzureOpenAI case), skip it
        elif chunk.choices[0].delta.content is None and not content_received:
            continue"""
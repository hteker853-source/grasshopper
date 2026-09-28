"""AWS Bedrock converse API. boto3 is imported only when a call is made."""

from __future__ import annotations

from grasshopper.providers.base import ProviderError


class BedrockLLM:
    name = "bedrock"

    def __init__(self, *, region: str, access_key: str, secret_key: str, model_id: str):
        self.region = region
        self.access_key = access_key
        self.secret_key = secret_key
        self.model_id = model_id

    def configured(self) -> bool:
        return bool(self.region and self.access_key and self.secret_key and self.model_id)

    async def complete(self, prompt: str, *, tier: str = "strong", system: str = "") -> str:
        if not self.configured():
            raise ProviderError("Bedrock is missing AWS_REGION, credentials, or BEDROCK_MODEL_ID")
        try:
            import boto3
        except ImportError as exc:
            raise ProviderError("boto3 is not installed (pip install -r requirements-real.txt)") from exc
        client = boto3.client(
            "bedrock-runtime",
            region_name=self.region,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        )
        body = {
            "messages": [{"role": "user", "content": [{"text": prompt}]}],
        }
        if system:
            body["system"] = [{"text": system}]
        result = client.converse(modelId=self.model_id, **body)
        parts = result["output"]["message"]["content"]
        return "".join(part.get("text", "") for part in parts)

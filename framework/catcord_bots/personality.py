from __future__ import annotations
import json
import re
import time
from typing import Any, Dict, Optional

import httpx


class PersonalityRenderer:
    def __init__(
        self,
        prompt_composer_url: str,
        character_id: str,
        cathy_api_url: str,
        fallback_system_prompt: str,
        cathy_api_key: Optional[str] = None,
        timeout_seconds: float = 60,
        connect_timeout_seconds: float = 3,
        max_tokens: int = 180,
        temperature: float = 0.2,
        top_p: float = 0.9,
        min_seconds_between_calls: int = 0,
        cathy_api_mode: str = "ollama",
        cathy_api_model: str = "gemma2:2b",
    ):
        self.prompt_composer_url = prompt_composer_url
        self.character_id = character_id
        self.cathy_api_url = cathy_api_url
        self.fallback_system_prompt = fallback_system_prompt
        self.cathy_api_key = cathy_api_key
        self.timeout_seconds = timeout_seconds
        self.connect_timeout_seconds = connect_timeout_seconds
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.min_seconds_between_calls = min_seconds_between_calls
        self.cathy_api_mode = cathy_api_mode
        self.cathy_api_model = cathy_api_model
        self._last_call_ts: float = 0.0

    def _rate_limited(self) -> bool:
        now = time.time()
        if (now - self._last_call_ts) < self.min_seconds_between_calls:
            return True
        self._last_call_ts = now
        return False

    async def _compose_prompt(self, client: httpx.AsyncClient, summary_payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call prompt-composer to build system prompt and messages."""
        mode = summary_payload.get("mode", "unknown")
        task = "pressure_status" if mode == "pressure" else "retention_report"
        
        body = {
            "task": task,
            "platform": "matrix",
            "character_id": self.character_id,
            "task_inputs": summary_payload,
        }
        
        url = f"{self.prompt_composer_url.rstrip('/')}/v1/prompt/compose"
        try:
            print(f"PersonalityRenderer: calling prompt-composer task={task}", flush=True)
            r = await client.post(url, json=body)
            r.raise_for_status()
            data = r.json()
            print(f"PersonalityRenderer: composer returned {len(json.dumps(data))} bytes", flush=True)
            return data
        except httpx.TimeoutException as e:
            print(f"PersonalityRenderer: composer timeout: {e!r}", flush=True)
            return None
        except httpx.HTTPStatusError as e:
            print(f"PersonalityRenderer: composer HTTP error: {e.response.status_code}", flush=True)
            return None
        except Exception as e:
            print(f"PersonalityRenderer: composer error: {e!r}", flush=True)
            return None

    async def _call_llm(self, client: httpx.AsyncClient, messages: list) -> Optional[str]:
        """Call LLM with messages and return prefix text."""
        headers = {"Content-Type": "application/json"}
        if self.cathy_api_key:
            headers["Authorization"] = f"Bearer {self.cathy_api_key}"
        
        try:
            if self.cathy_api_mode.lower() == "ollama":
                body = {
                    "model": self.cathy_api_model,
                    "stream": False,
                    "messages": messages,
                    "options": {
                        "temperature": 0.2,
                        "num_predict": 32,
                        "num_ctx": 384,
                        "stop": ["\n"],
                    },
                }
                r = await client.post(
                    f"{self.cathy_api_url.rstrip('/')}/api/chat",
                    headers=headers,
                    json=body,
                )
                r.raise_for_status()
                data = r.json()
                prefix = (data.get("message") or {}).get("content", "").strip()
            else:
                body = {
                    "model": self.cathy_api_model,
                    "messages": messages,
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                    "max_tokens": self.max_tokens,
                    "stream": False,
                }
                r = await client.post(
                    f"{self.cathy_api_url.rstrip('/')}/v1/chat/completions",
                    headers=headers,
                    json=body,
                )
                r.raise_for_status()
                data = r.json()
                prefix = (
                    data.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                    .strip()
                )
            
            prefix = prefix.strip().strip('"').strip("'").strip()
            if prefix and "\n" in prefix:
                prefix = prefix.split("\n", 1)[0].strip()
            
            return prefix if prefix else None
            
        except httpx.TimeoutException as e:
            print(f"PersonalityRenderer: LLM timeout: {e!r}", flush=True)
            return None
        except httpx.HTTPStatusError as e:
            print(f"PersonalityRenderer: LLM HTTP error: {e.response.status_code}", flush=True)
            return None
        except Exception as e:
            print(f"PersonalityRenderer: LLM error: {e!r}", flush=True)
            return None

    def _validate_prefix(self, text: str) -> tuple[bool, str]:
        """Validate AI prefix is safe and contains no numbers."""
        t = text.strip()
        tlow = t.lower()

        if not t:
            return False, "empty"
        if "\n" in t:
            return False, "newline"
        if len(t) > 180:
            return False, "too long"
        if re.search(r"[.!?].+[A-Z]", t):
            return False, "likely multiple sentences"

        bad_ack = ["ok", "understood", "please provide"]
        if any(tlow.startswith(x) for x in bad_ack):
            return False, "acknowledgement/assistant filler"

        banned = ["today", "yesterday", "uptime", "operational since", "elapsed"]
        for b in banned:
            if re.search(rf"\b{re.escape(b)}\b", tlow):
                return False, f"banned phrase '{b}'"

        if re.search(r"\d", t):
            return False, "contains digits"

        bad_actions = ["deleted", "removed", "purged", "redacted", "cleared"]
        if any(w in tlow for w in bad_actions):
            return False, "claims deletion"

        return True, ""

    async def render(self, summary_payload: Dict[str, Any]) -> Optional[str]:
        """Render AI prefix using prompt-composer and LLM."""
        if self._rate_limited():
            return None

        try:
            timeout = httpx.Timeout(
                connect=self.connect_timeout_seconds,
                read=self.timeout_seconds,
                write=self.timeout_seconds,
                pool=self.timeout_seconds,
            )

            async with httpx.AsyncClient(timeout=timeout) as client:
                prompt_bundle = await self._compose_prompt(client, summary_payload)
                if not prompt_bundle:
                    print("PersonalityRenderer: no prompt bundle, skipping AI", flush=True)
                    return None
                
                messages = prompt_bundle.get("messages")
                if not messages:
                    system_text = prompt_bundle.get("system_text", "")
                    if not system_text:
                        print("PersonalityRenderer: empty prompt bundle, skipping AI", flush=True)
                        return None
                    messages = [
                        {"role": "system", "content": system_text},
                        {"role": "user", "content": "Provide status update."}
                    ]
                
                for attempt in range(2):
                    prefix = await self._call_llm(client, messages)
                    if not prefix:
                        print(f"PersonalityRenderer: empty LLM response (attempt={attempt})", flush=True)
                        if attempt == 0:
                            continue
                        return None
                    
                    ok, reason = self._validate_prefix(prefix)
                    if not ok:
                        print(f"PersonalityRenderer: rejected prefix (attempt={attempt}) reason={reason} prefix={prefix[:100]!r}", flush=True)
                        if attempt == 0:
                            messages.append({
                                "role": "user",
                                "content": (
                                    f"Your previous response violated a rule: {reason}\n"
                                    "Rewrite as ONE sentence. No digits, no percentages, no GB, no timestamps, no quotes."
                                )
                            })
                            continue
                        return None
                    
                    print(f"PersonalityRenderer: accepted prefix={prefix!r}", flush=True)
                    return prefix
                
                return None

        except Exception as e:
            print(f"PersonalityRenderer: render exception: {e!r}", flush=True)
            return None

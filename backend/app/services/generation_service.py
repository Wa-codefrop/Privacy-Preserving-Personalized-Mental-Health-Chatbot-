from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.core.config import settings


@dataclass
class GenerationConfig:
    backend: str = "local"
    local_model_path: str | None = None
    device: str = "auto"
    max_new_tokens: int = 180
    temperature: float = 0.7
    do_sample: bool = True
    use_lora: bool = False
    lora_r: int = 8
    lora_alpha: int = 16
    lora_target_modules: list[str] = field(
        default_factory=lambda: ["q_proj", "v_proj"]
    )


class GenerationService:
    def __init__(
        self,
        local_model_path: str | None = None,
        config: GenerationConfig | None = None,
        default_response: str | None = None,
    ) -> None:
        self.config = config or GenerationConfig(
            backend=settings.generation_backend,
            local_model_path=local_model_path or settings.local_generation_model,
            device=settings.generation_device,
            max_new_tokens=settings.generation_max_new_tokens,
            temperature=settings.generation_temperature,
            do_sample=settings.generation_do_sample,
            use_lora=settings.lora_enabled,
            lora_r=settings.lora_r,
            lora_alpha=settings.lora_alpha,
            lora_target_modules=settings.lora_target_modules,
        )
        self.default_response = default_response or (
            "I can listen and support you, but I am not a clinician or emergency responder. "
            "Please tell me what feels most important right now and what support would help."
        )
        self._local_pipeline: Any | None = None

    def _load_local_pipeline(self) -> Any | None:
        if self._local_pipeline is not None:
            return self._local_pipeline
        if not self.config.local_model_path:
            return None
        model_path = Path(self.config.local_model_path)
        if not model_path.exists():
            return None
        try:
            from transformers import pipeline
        except ImportError:
            return None
        try:
            device = self.config.device if self.config.device != "auto" else None
            self._local_pipeline = pipeline(
                "text-generation",
                model=str(model_path),
                device_map=device,
            )
        except Exception:
            return None
        return self._local_pipeline

    def generate(self, prompt: str, **kwargs: Any) -> str:
        local_pipeline = self._load_local_pipeline()
        if local_pipeline is not None:
            try:
                generation_kwargs = {
                    "max_new_tokens": kwargs.get("max_new_tokens", self.config.max_new_tokens),
                    "temperature": kwargs.get("temperature", self.config.temperature),
                    "do_sample": kwargs.get("do_sample", self.config.do_sample),
                    "return_full_text": False,
                }
                outputs = local_pipeline(prompt, **generation_kwargs)
                if outputs and isinstance(outputs, list):
                    generated = outputs[0].get("generated_text")
                    if generated:
                        return str(generated).strip() or self.default_response
            except Exception:
                pass
        return self.default_response

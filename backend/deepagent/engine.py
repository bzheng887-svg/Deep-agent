from typing import Optional, Dict, Any

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

from backend.config import *

def _apply_profile(model: BaseChatModel, context_window: int) -> BaseChatModel:
    """Set model profile so deepagents SummarizationMiddleware can auto-compute
    context window thresholds (trigger / keep) using fraction-based settings."""
    if hasattr(model, "profile"):
        if not model.profile or "max_input_tokens" not in model.profile:
            model.profile = {"max_input_tokens": context_window}
    return model


def get_llm_model(
    config: Optional[Dict[str, Any]] = None,
    max_tokens_override: Optional[int] = None,
    streaming: bool = True,
) -> BaseChatModel:
    """
    构建 LLM 模型实例。

    Args:
        config: ModelConfig 字典（可选），含 model_name, base_url, api_key, context_window 等。
                为 None 时使用 settings 中的默认值。
        max_tokens_override: 覆盖默认 max_tokens（来自用户任务设置）。
        streaming: 是否用于流式调用。为 True 时附带 stream_options 以获取 token 统计，
                   为 False 时不传 stream_options（某些 API 在非流式调用时不接受该参数）。
    """
    effective_max_tokens = max_tokens_override or max_tokens

    # stream_options 仅在流式调用时传递，非流式调用时 API 会拒绝该参数
    extra_kwargs: Dict[str, Any] = {}
    if streaming:
        extra_kwargs["stream_options"] = {"include_usage": True}

    if config:
        model_name = config.get("model_name", model_ds_name)
        provider = config.get("provider", "openai")
        # ---- -------- -------- -------- -------- -------- ----

        # ctx_window = _resolve_context_window(
        #     model_name,
        #     explicit=config.get("context_window"),
        # )
        ctx_window = config.get("context_window", context_window)
        # ---- -------- -------- -------- -------- -------- ----

        # if provider == "gemini":
        #     api_key = config.get("api_key") or settings.model_ds_api_key
        #     model = _create_gemini_model(
        #         model_name=model_name,
        #         api_key=api_key,
        #         max_tokens=effective_max_tokens,
        #         streaming=streaming,
        #         extra_kwargs=extra_kwargs,
        #     )
        #     return _apply_profile(model, ctx_window)

        model = ChatOpenAI(
            model=model_name,
            base_url=config.get("base_url") or model_ds_base_url,
            api_key=config.get("api_key") or model_ds_api_key,
            max_tokens=effective_max_tokens,
            max_retries=3,
            request_timeout=120,
            model_kwargs=extra_kwargs,
        )
        return _apply_profile(model, ctx_window)

    # ctx_window = _resolve_context_window(
    #     settings.model_ds_name,
    #     explicit=settings.context_window,
    # )
    ctx_window = context_window

    model = ChatOpenAI(
        model=model_ds_name,
        base_url=model_ds_base_url,
        api_key=model_ds_api_key,
        max_tokens=effective_max_tokens,
        max_retries=3,
        request_timeout=120,
        model_kwargs=extra_kwargs,
    )
    return _apply_profile(model, ctx_window)

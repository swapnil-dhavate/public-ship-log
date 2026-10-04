"""Minimal Telegram Bot API client."""
from . import env, net


def token():
    return env.get("TELEGRAM_BOT_TOKEN")


def owner_chat():
    return env.get("TELEGRAM_CHAT_ID")


def api(method, timeout=30, **params):
    if not token():
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
    params = {k: v for k, v in params.items() if v is not None}
    resp = net.post(f"https://api.telegram.org/bot{token()}/{method}", params, timeout=timeout)
    if not resp.get("ok"):
        raise RuntimeError(f"Telegram {method} failed: {resp}")
    return resp["result"]


def send(text, chat_id=None, buttons=None):
    """Send an HTML-formatted message. buttons = [[(label, callback_data), ...], ...]"""
    markup = None
    if buttons:
        markup = {"inline_keyboard": [[{"text": t, "callback_data": d} for t, d in row] for row in buttons]}
    return api("sendMessage", chat_id=chat_id or owner_chat(), text=text, parse_mode="HTML",
               reply_markup=markup, disable_web_page_preview=True)


def edit(chat_id, message_id, text, buttons=None):
    markup = {"inline_keyboard": [[{"text": t, "callback_data": d} for t, d in row] for row in buttons or []]}
    return api("editMessageText", chat_id=chat_id, message_id=message_id, text=text,
               parse_mode="HTML", reply_markup=markup, disable_web_page_preview=True)


def answer_callback(callback_id, text=""):
    try:
        api("answerCallbackQuery", callback_query_id=callback_id, text=text)
    except Exception:
        pass  # old callbacks can't be answered any more; harmless


def get_updates(offset=None, wait=0):
    """Fetch new updates; wait > 0 long-polls up to that many seconds."""
    if not token():
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
    payload = {"timeout": wait, "allowed_updates": ["message", "callback_query"]}
    if offset is not None:
        payload["offset"] = offset
    resp = net.post(f"https://api.telegram.org/bot{token()}/getUpdates", payload, timeout=wait + 15)
    if not resp.get("ok"):
        raise RuntimeError(f"Telegram getUpdates failed: {resp}")
    return resp["result"]

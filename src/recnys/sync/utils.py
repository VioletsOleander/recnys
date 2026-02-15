__all__ = ["prompt_for_confirmation"]


def prompt_for_confirmation(message: str, confirm_signal: str) -> bool:
    response = input(message).strip().lower()
    return response == confirm_signal

from sqlalchemy import exc as error


def is_unique_violation(e: error.IntegrityError) -> bool:
    msg = str(getattr(e, "orig", e)).lower()
    return "unique" in msg or "duplicate" in msg


__all__ = ["is_unique_violation"]

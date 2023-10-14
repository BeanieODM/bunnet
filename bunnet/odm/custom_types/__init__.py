from bunnet.odm.utils.pydantic import IS_PYDANTIC_V2

if IS_PYDANTIC_V2:
    from bunnet.odm.custom_types.decimal import DecimalAnnotation
else:
    from decimal import Decimal as DecimalAnnotation

__all__ = [
    "DecimalAnnotation",
]

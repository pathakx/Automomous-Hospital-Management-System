from pydantic import BaseModel
from typing import Optional, Any


class ToolResult(BaseModel):
    """
    Universal return type for all Week 5 tool functions.

    Attributes:
        success:   True if the tool executed without errors.
        data:      The actual result payload (list, dict, or any value).
                   Is None when success=False.
        error:     A machine-readable error code string when success=False.
                   Is None when success=True.

    Usage Examples:
        # Success case
        return ToolResult(success=True, data={"bills": [...]})

        # Failure case
        return ToolResult(success=False, error="report_not_found")
    """
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None

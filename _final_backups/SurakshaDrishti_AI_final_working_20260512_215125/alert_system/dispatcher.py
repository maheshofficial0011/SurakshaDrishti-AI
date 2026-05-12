"""
SurakshaDrishti AI — Alert Dispatcher

Purpose:
- Central alert dispatch point used by the Event Engine.
- In the final MVP, dashboard/backend delivery is handled by the pipeline
  through the FastAPI /events endpoint.
- This dispatcher intentionally avoids noisy terminal printing.

Why quiet mode?
- The tracking pipeline already prints clean formatted alerts using
  utils.terminal.print_alert().
- If this dispatcher also prints alerts, the terminal becomes duplicated
  and messy.
"""


class AlertDispatcher:
    """
    Lightweight alert dispatcher for final MVP.

    Current behavior:
    - Accepts event dictionaries from EventEngine.
    - Does not print noisy blocks.
    - Does not send duplicate backend requests.
    - Keeps the interface stable: self.alert.send(event)

    Future expansion:
    - Email alerts
    - Telegram alerts
    - SMS alerts
    - Push notifications
    """

    def __init__(self, verbose=False):
        """
        Args:
            verbose:
                If True, prints a very small debug message.
                Keep False for final MVP clean terminal mode.
        """

        self.verbose = verbose

    def send(self, event):
        """
        Dispatch an alert event.

        Final MVP:
        This function is intentionally quiet because the main pipeline handles:
        - clean terminal alert display
        - backend API submission
        - dashboard WebSocket broadcast through backend

        Args:
            event: dict containing alert data

        Returns:
            True if accepted by dispatcher.
        """

        if not event:
            return False

        if self.verbose:
            event_type = event.get("type", "UNKNOWN")
            severity = event.get("severity", "INFO")
            print(f"[DISPATCHER] {event_type} | {severity}")

        return True

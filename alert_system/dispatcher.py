class AlertDispatcher:

    def send(self, event):
        """
        Central alert handler (Phase 5 core)
        Later we plug:
        - Telegram
        - SMS
        - Firebase
        """

        print("\n🚨 ALERT TRIGGERED")
        print("Type:", event["type"])

        if "zone" in event:
            print("Zone:", event["zone"])

        if "object_id" in event:
            print("Object ID:", event["object_id"])

        print("----------------------\n")
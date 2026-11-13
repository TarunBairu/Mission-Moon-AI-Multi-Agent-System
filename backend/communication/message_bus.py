from datetime import datetime
from uuid import uuid4


class MessageBus:

    def __init__(self):

        self.messages = []

        self.total_messages = 0

    # ======================================
    # SEND MESSAGE
    # ======================================

    def send_message(self, sender, receiver, message):

        message_data = {

            "message_id": str(uuid4()),

            "sender": sender,

            "receiver": receiver,

            "message": message,

            "timestamp": datetime.now().isoformat(),

            "status": "Delivered"
        }

        self.messages.append(message_data)

        self.total_messages += 1

        return message_data

    # ======================================
    # GET MESSAGES
    # ======================================

    def get_messages(self, receiver=None):

        if receiver:

            return [

                message

                for message in self.messages

                if message["receiver"] == receiver
                or message["receiver"] == "All"

            ]

        return self.messages

    # ======================================
    # GET AGENT COMMUNICATION HISTORY
    # ======================================

    def get_agent_messages(self, agent_name):

        return [

            message

            for message in self.messages

            if message["sender"] == agent_name
            or message["receiver"] == agent_name
            or message["receiver"] == "All"

        ]

    # ======================================
    # GET MESSAGE STATISTICS
    # ======================================

    def get_statistics(self):

        return {

            "total_messages": self.total_messages,

            "delivered_messages": sum(
                1 for message in self.messages
                if message["status"] == "Delivered"
            )

        }

    # ======================================
    # CLEAR MESSAGE HISTORY
    # ======================================

    def clear_messages(self):

        self.messages.clear()

        self.total_messages = 0
import os
from typing import Optional
from mem0 import MemoryClient

from dotenv import load_dotenv
load_dotenv()

from core.memory.objectbox_memory import Database

class MemoryService:
    def __init__(
            self,
            mem0_api_key: Optional[str] = None,
            path: Optional[str] = None
    ):
        if not mem0_api_key:
            mem0_api_key = os.getenv("MEM0_API_KEY")
        if not path:
            path = '../../db'

        self.mem0_client = MemoryClient(api_key=mem0_api_key)
        self.reminders = Database(path)

    """ --- Mem0 --- """

    def memory_add(self, memory, user_id):
        return self.mem0_client.add(messages=memory, user_id=user_id, version="v2", output_format="v1.1")

    def memory_update(self, memory, memory_id):
        return self.mem0_client.update(text=memory, memory_id=memory_id)

    def memory_delete(self, memory_id):
        return self.mem0_client.delete(memory_id=memory_id)

    def memory_retrieve(self, user_id):
        return self.mem0_client.get_all(user_id=user_id)

    """ --- ObjectBox --- """

    def objectbox_add(self, memory):
        return self.reminders.add_objectbox(memory)

    def objectbox_update(self, memory, memory_id):
        return self.reminders.update_objectbox(memory=memory, ide=int(memory_id))

    def objectbox_remove(self, memory_id):
        return self.reminders.remove_objectbox(int(memory_id))

    def objectbox_retrieve(self, query):
        return self.reminders.retrieve_objectbox(query)

    def objectbox_get_all(self):
        return self.reminders.list_all()

    def objectbox_close(self) -> None:
        self.reminders.close()
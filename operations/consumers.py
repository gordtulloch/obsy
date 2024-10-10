# consumers.py
import os
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer

class LogConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.logfile_path = 'test.log'
        self.logfile = open(self.logfile_path, 'r')
        self.logfile.seek(0, os.SEEK_END)
        self.keep_reading = True
        asyncio.create_task(self.send_log_updates())

    async def disconnect(self, close_code):
        self.keep_reading = False
        self.logfile.close()

    async def send_log_updates(self):
        while self.keep_reading:
            line = self.logfile.readline()
            if line:
                await self.send(text_data=line)
            else:
                await asyncio.sleep(1)
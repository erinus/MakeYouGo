# MakeYouGo

4 systems:

1. WEB Server<br/>
   server.py
   Web UI for user contro, system administration, and module management

2. API Server
   server.py
   API for module combination and other service access

3. Tasker
   tasker.py
   Execute cron job and loop task

4. RabbitMQ Client
   Make device connect with our service and receive remote control through NAT

# cowin-alerts

Schedule the job in crontab like below ( Runs every minute ). You can also Schedule the way you want 
```
crontab -e
* * * * * cd /COWIN-Alerts&& python main.py > cron-cowin-selective.logs
```

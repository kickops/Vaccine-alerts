# cowin-alerts

Schedule the job in crontab like below ( Runs every minute ). You can also Schedule the way you want 
```
crontab -e
* * * * * cd /Vaccine-alerts && python main.py > cron-cowin.logs
```

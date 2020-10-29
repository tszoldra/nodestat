import psutil
import json

usernames = [user.name for user in psutil.users()]
virtual_memory = psutil.virtual_memory()._asdict()
cpu_count_logical = psutil.cpu_count(logical=True)
cpu_count_physical = psutil.cpu_count(logical=False)
cpu_freq = psutil.cpu_freq()._asdict()
cpu_times = psutil.cpu_times()._asdict()
cpu_percent = psutil.cpu_percent(percpu=False)
cpu_percent_percpu = psutil.cpu_percent(percpu=True)

for x in [usernames, virtual_memory,
          cpu_count_logical, cpu_count_physical, cpu_freq,
          cpu_times, cpu_percent, cpu_percent_percpu]:
    print(json.dumps(x))

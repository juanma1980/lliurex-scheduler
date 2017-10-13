#!/usr/bin/env python3
from clientScheduler import clientScheduler as scheduler

s=scheduler()
a=s.get_scheduled_tasks('remote')
#s.write_tasks(a)
print(a)

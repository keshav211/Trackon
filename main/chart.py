import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from datetime import datetime
import os
plt.style.use("seaborn")


def line_plot(tracker_stats):
    x, y = [], []
    for log in tracker_stats:
        log_date = str(log["task_date"])[0:-10]
        test = datetime.strptime(log_date,'%Y-%m-%d %H:%M')
        test=str(test)
        x.append(test)
        y.append(float(log["task_value"]))
    
    plt.clf()
    plt.plot_date(x, y, linestyle="solid")
    plt.gcf().autofmt_xdate()
    plt.savefig("./main/static/graph.png")



import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from datetime import datetime
import os
plt.style.use("seaborn")


def line_plot(tracker_stats):
    x, y = [], []
    for log in tracker_stats:
        log_date = str(log["task_date"])
        test = datetime.strptime(log_date,'%Y-%m-%d %H:%M:%S')
        test=str(test)
        x.append(test)
        y.append(float(log["task_value"]))
    
    plt.clf()
    plt.plot_date(x, y, linestyle="solid")
    plt.gcf().autofmt_xdate()
    plt.savefig("./main/static/graph.png")




def pie_chart(tracker_stats):
    value_counts = dict()
    for log in tracker_stats:
        value_counts[log["task_value"]] = value_counts.get(log["task_value"], 0) + 1
    labels = value_counts.keys()
    counts = value_counts.values()
    explode = tuple([0.03 for i in range(len(labels))])        # only "explode" the 2nd slice

    plt.clf()
    plt.pie(counts, labels=labels, explode=explode, autopct='%1.1f%%')
    plt.savefig("./main/static/graph.png")
import numpy as np
import matplotlib.pyplot as plt


def plot_two_y_axis_line_chart(path, x, ys, labels, title, x_label, y1_label, y2_label):
    plt.clf()
    fig, ax1 = plt.subplots()
    for y, label in zip(ys['prec'], labels['prec']):
        ax1.plot(x, y, label=label)
    plt.legend()
    ax2 = ax1.twinx()
    for y, label in zip(ys['num'], labels['num']):
        ax2.plot(x, y, '--y', label=label)

    plt.title(title, fontweight='bold', fontsize=10)
    ax1.set_xlabel(x_label, fontweight='bold', fontsize=8)
    ax1.set_ylabel(y1_label, fontweight='bold', fontsize=8)
    ax2.set_ylabel(y2_label, fontweight='bold', fontsize=8)
    ax2.set_yticks(ticks=y)
    plt.xticks(ticks=x, labels=x)
    plt.legend()
    # plt.savefig(path)
    return plt

def plot_multi_line_chart_TIRPS(xs, ys, labels, title, x_label='Time Line', y_label='Intervals'):
    plt.clf()
    plt.figure(figsize=(6, 4))
    for x, y, label in zip(xs, ys, labels):
        plt.plot(x, y, '-o', label=label, linewidth=8)
    plt.title(title, fontweight='bold', fontsize=14)
    plt.xlabel(x_label, fontweight='bold', fontsize=10)
    plt.ylabel(y_label, fontweight='bold', fontsize=10)
    plt.yticks(ticks=labels, labels=[''] * len(labels))
    plt.subplots_adjust(left=0.08, bottom=0.25, right=0.92, top=0.8)
    plt.margins(y=0.5)
    plt.legend(loc=1)
    plt.show()


def plot_multi_line_chart(path, x, ys, labels, title, x_label, y_label):
    plt.clf()
    plt.figure(figsize=(6, 6))
    for y, label in zip(ys, labels):
        plt.plot(x, y, '-o', label=label)

    plt.title(title, fontweight='bold', fontsize=12)
    plt.xlabel(x_label, fontweight='bold', fontsize=12)
    plt.ylabel(y_label, fontweight='bold', fontsize=12)
    plt.xticks(ticks=x, labels=x)
    # plt.xticks(rotation=20, fontweight='bold', fontsize=12)
    plt.legend()
    plt.savefig(path)
    # return plt


def time_line_chart(path, x, y, title, x_label, y_label):
    plt.clf()
    plt.plot(x, y)
    # plt.title(title, fontweight='bold', fontsize=12)
    plt.xlabel(x_label, fontweight='bold', fontsize=12)
    plt.ylabel(y_label, fontweight='bold', fontsize=12)
    plt.xticks(ticks=x, labels=x)
    y_t = [yi for yi in range(int(max(y)+2))]
    if len(y_t) > 10:
        y_t = [yi for yi in range(0, int((max(y)+2)/10)*12, int((max(y)+2)/10))]
    plt.yticks(ticks=y_t, labels=y_t)
    plt.savefig(path)

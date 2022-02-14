import matplotlib.pyplot as plt


def create_at_groups(path, x_labels, bins_count, at_var, color='lightskyblue'):
    plt.clf()
    plt.figure(figsize=(8, 10))
    labels = [f'{round(100 * count / sum(bins_count), 2)}%' for count in bins_count]
    bar = plt.bar(x_labels, bins_count, 0.9, color=color)
    plt.bar_label(bar, labels, label_type='center', fontweight='bold', fontsize=14)
    plt.xticks(rotation=20, fontweight='bold', fontsize=12)
    plt.yticks(fontweight='bold', fontsize=10)
    plt.xlabel('ATemporal Variable Groups', fontweight='bold', fontsize=12)
    plt.ylabel('Count', fontweight='bold', fontsize=12)
    plt.title(f'{at_var.upper()} Distribution', fontweight='bold', fontsize=16)
    plt.savefig(path)
    plt.show()
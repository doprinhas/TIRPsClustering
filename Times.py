from datetime import datetime as dt
import Globals as Glob

times_paths = {
    'Dataset': '',
    'Current Exp': ''
}


def write_to_dataset_times(line):
    write_to_log(line, log_paths['Dataset'])


def write_to_experiment_times(line):
    write_to_log(line, log_paths['Current Exp'])


def write_to_times(out_dir_path, line, form='a'):
    file = open(f'{out_dir_path}Times.txt', form)
    file.write(f'{line}\n')
    file.close()
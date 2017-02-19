"""various helper functions"""
# coding=utf-8
import subprocess
import time

import numpy as np

epsilon_0 = 1


def l2_norm(reference: np.ndarray, test: np.ndarray) -> float:
    # noinspection PyTypeChecker
    return np.sum((reference - test) ** 2) / np.sum(reference ** 2)


def l2_test(reference: np.ndarray, test: np.ndarray, rtol: float = 1e-3) -> bool:
    norm = l2_norm(reference, test)
    print("L2 norm: ", norm)
    return norm < rtol


def date_version_string() -> str:
    run_time = time.ctime()
    git_version = subprocess.check_output(['git', 'describe', '--always']).decode()[:-1]
    dv_string = "{}\nPrevious git version: {}".format(run_time, git_version)
    return dv_string


if __name__ == "__main__":
    print(date_version_string())


def read_hdf5_group(group):
    print("Group:", group)
    for i in group:
        print(i, group[i])
    for attr in group.attrs:
        print(attr, group.attrs[attr])

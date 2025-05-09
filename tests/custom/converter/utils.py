import math
import os


def almost_equal_1d(a, b, tol=1e-9):
    return all(math.isclose(x, y, abs_tol=tol) for x, y in zip(a, b))


def almost_equal_2d(a, b, tol=1e-9):
    a = [z for x in a for z in x]
    b = [z for x in b for z in x]
    return all(math.isclose(x, y, abs_tol=tol) for x, y in zip(a, b))


def check_equal_list_of_strings(list1, list2):
    # Check that both lists are not empty
    if not list1 or not list2:
        return False

    list1.sort()
    list2.sort()

    # Check that the lists have the same length
    if len(list1) != len(list2):
        return False

    # Check that the elements of the lists are equal
    for i in range(len(list1)):
        if list1[i] != list2[i]:
            return False

    return True


def get_os_walk(root_path):
    list_file_paths = []
    for root, dirs, files in os.walk(root_path):
        for f in files:
            list_file_paths += [os.path.join(root, f)]
    return list_file_paths

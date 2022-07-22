import os
import csv
import random
import json
import time
import itertools
from pathlib import Path
from tqdm import tqdm


class timer(object):
    def __init__(self):
        self.start = None

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, type, value, traceback):
        print('took {} seconds'.format(time.time() - self.start))


def load_json(path):
    with open(path, 'r', encoding="utf-8") as f:
        return json.load(f)


def iterate(data, take_n=None, sample_ratio=1.0, sample_seed=None, silent=False):
    '''
    base iterator handler
    :param data: iterator
    :param take_n: stop the iterator after taking the first n items
    :param sample_ratio: probability of keep an item
    :param sample_seed: seed for sampling
    :param silent: should use tqdm or not
    :return: iteraotr
    '''
    if sample_seed is not None:
        random.seed(sample_seed)
    if take_n is not None:
        assert take_n >= 1, 'take_n should be >= 1'
    for d in tqdm(itertools.islice(data, 0, take_n), disable=silent):
        if random.random() <= sample_ratio:
            yield d


def load_jsonl(path, encoding="utf-8", take_n=None, sample_ratio=1.0, sample_seed=None, silent=False):
    with open(path, 'r', encoding=encoding) as f:
        for line in iterate(f, take_n, sample_ratio, sample_seed, silent):
            yield json.loads(line)


def load_txt(path, encoding="utf-8", take_n=None, sample_ratio=1.0, sample_seed=None, silent=False):
    with open(path, 'r', encoding=encoding) as f:
        for line in iterate(f, take_n, sample_ratio, sample_seed, silent):
            yield line.rstrip()


def load_csv(path, encoding="utf-8", delimiter=',', take_n=None, sample_ratio=1.0, sample_seed=None, silent=False):
    csv.field_size_limit(10000000)
    with open(path, 'r', encoding=encoding) as f:
        for d in iterate(csv.reader(f, delimiter=delimiter), take_n, sample_ratio, sample_seed, silent):
            yield d


def load_tsv(path, encoding="utf-8", take_n=None, sample_ratio=1.0, sample_seed=None, silent=False):
    csv.field_size_limit(10000000)
    for d in load_csv(path, encoding, '/t', take_n, sample_ratio, sample_seed, silent):
        yield d


def build_table(rows, column_names=None, columns_gap_size=3):
    assert columns_gap_size >= 1, 'column_gap_size must be >= 1'

    num_col = None
    for row in rows:
        if num_col is None:
            num_col = len(row)
        else:
            assert num_col == len(row), 'rows have different size'

    if column_names is not None:
        rows = [column_names] + [[str(r) for r in row] for row in rows]

    sizes = [0] * num_col
    for row in rows:
        assert len(row) <= num_col
        for i, item in enumerate(row):
            sizes[i] = max(sizes[i], len(item))

    res = []
    for row in rows:
        stuff = []
        for i in range(num_col - 1):
            stuff.append(row[i])
            stuff.append(' ' * (columns_gap_size + sizes[i] - len(row[i])))
        stuff.append(row[-1])
        line = ''.join(stuff)
        res.append(line)
    return res


def print_list(data):
    for item in data:
        print(item)


def print_table(rows, column_names=None, columns_gap_size=3):
    print_list(build_table(rows, column_names, columns_gap_size))


def min_max_avg(vec):
    res_min, res_max, res_sum = float('inf'), -float('inf'), 0
    for num in vec:
        res_min = min(res_min, num)
        res_max = max(res_max, num)
        res_sum += num
    return res_min, res_max, res_sum / len(vec)


def sep(text, size=10, char='-'):
    wing = char * size
    print(wing + text + wing)


class text_block(object):
    def __init__(self, text, size=10, char='-', y_gap_size=1):
        self.text = text
        self.size = size
        self.char = char
        self.y_gap_size = y_gap_size

    def __enter__(self):
        print('\n' * self.y_gap_size, end="")
        sep(self.text, self.size, self.char)

    def __exit__(self, type, value, traceback):
        print(self.char * (self.size * 2 + len(self.text)))
        print('\n' * self.y_gap_size, end="")


def aetk_path():
    return __file__


def aetk_dir():
    return dir_of(aetk_path())


def dir_of(file):
    return str(Path(file).parent.absolute())


def running_dir():
    return os.getcwd()


def show_examples():
    with text_block('aetk_examples', char='=', y_gap_size=2):
        for line in load_txt(os.path.join(aetk_dir(), 'aetk_examples.py'), silent=True):
            print(line)


if __name__ == '__main__':
    show_examples()
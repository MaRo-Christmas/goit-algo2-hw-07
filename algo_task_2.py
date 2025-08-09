from __future__ import annotations

import argparse
import timeit
from functools import lru_cache
from dataclasses import dataclass
from typing import List, Tuple
import matplotlib.pyplot as plt
import sys

sys.setrecursionlimit(1_000_000)

MAX_RECURSIVE_N = 400

@dataclass
class Node:
    key: int
    value: int
    left: "Node" = None
    right: "Node" = None

class SplayTree:
    def __init__(self):
        self.root: Node | None = None

    def _rotate_right(self, x: Node) -> Node:
        y = x.left
        x.left = y.right
        y.right = x
        return y

    def _rotate_left(self, x: Node) -> Node:
        y = x.right
        x.right = y.left
        y.left = x
        return y

    def _splay(self, root: Node | None, key: int) -> Node | None:
        if root is None or root.key == key:
            return root

        if key < root.key:
            if root.left is None:
                return root
            if key < root.left.key:
                root.left.left = self._splay(root.left.left, key)
                root = self._rotate_right(root)
            elif key > root.left.key:
                root.left.right = self._splay(root.left.right, key)
                if root.left.right is not None:
                    root.left = self._rotate_left(root.left)
            return root if root.left is None else self._rotate_right(root)
        else:
            if root.right is None:
                return root
            if key > root.right.key:
                root.right.right = self._splay(root.right.right, key)
                root = self._rotate_left(root)
            elif key < root.right.key:
                root.right.left = self._splay(root.right.left, key)
                if root.right.left is not None:
                    root.right = self._rotate_right(root.right)
            return root if root.right is None else self._rotate_left(root)

    def search(self, key: int):
        self.root = self._splay(self.root, key)
        if self.root and self.root.key == key:
            return self.root.value
        return None

    def insert(self, key: int, value: int) -> None:
        if self.root is None:
            self.root = Node(key, value)
            return
        self.root = self._splay(self.root, key)
        if self.root.key == key:
            self.root.value = value
            return
        new = Node(key, value)
        if key < self.root.key:
            new.right = self.root
            new.left = self.root.left
            self.root.left = None
        else:
            new.left = self.root
            new.right = self.root.right
            self.root.right = None
        self.root = new

@lru_cache(maxsize=None)
def fibonacci_lru(n: int) -> int:
    if n < 2:
        return n
    if n <= MAX_RECURSIVE_N:
        return fibonacci_lru(n - 1) + fibonacci_lru(n - 2)
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
def fibonacci_splay(n: int, tree: SplayTree) -> int:
    hit = tree.search(n)
    if hit is not None:
        return hit

    for k in range(0, n + 1):
        if tree.search(k) is None:
            if k < 2:
                tree.insert(k, k)
            else:
                a = tree.search(k - 1)
                b = tree.search(k - 2)
                tree.insert(k, (a if a is not None else 0) + (b if b is not None else 0))
    return tree.search(n)

def measure_times(ns: List[int], repeats: int = 3) -> Tuple[List[float], List[float]]:
    lru_times: List[float] = []
    splay_times: List[float] = []

    for n in ns:
        def run_lru():
            fibonacci_lru.cache_clear()
            fibonacci_lru(n)

        lru_result = timeit.repeat(stmt=run_lru, repeat=repeats, number=1)
        lru_times.append(sum(lru_result) / repeats)

        def run_splay():
            tree = SplayTree()
            fibonacci_splay(n, tree)

        splay_result = timeit.repeat(stmt=run_splay, repeat=repeats, number=1)
        splay_times.append(sum(splay_result) / repeats)

    return lru_times, splay_times

def print_table(ns: List[int], lru_times: List[float], splay_times: List[float]) -> None:
    header = f"{'n':<8}{'LRU Cache Time (s)':>22}{'Splay Tree Time (s)':>22}"
    line = "-" * len(header)
    print(header)
    print(line)
    for n, t1, t2 in zip(ns, lru_times, splay_times):
        print(f"{n:<8}{t1:>22.8f}{t2:>22.8f}")

def plot_times(ns: List[int], lru_times: List[float], splay_times: List[float], png_path: str) -> None:
    plt.figure(figsize=(10, 6))
    plt.plot(ns, lru_times, marker="o", label="LRU Cache")
    plt.plot(ns, splay_times, marker="x", label="Splay Tree")
    plt.title("Порівняння часу виконання для LRU Cache та Splay Tree")
    plt.xlabel("Число Фібоначчі (n)")
    plt.ylabel("Середній час виконання (секунди)")
    plt.legend()
    plt.grid(True)
    plt.savefig(png_path, bbox_inches="tight")

def main():
    parser = argparse.ArgumentParser(description="Fibonacci: LRU cache vs Splay Tree benchmark")
    parser.add_argument("--nmax", type=int, default=950, help="Максимальне n (включно)")
    parser.add_argument("--step", type=int, default=50, help="Крок по n")
    parser.add_argument("--repeats", type=int, default=3, help="Кількість повторів для усереднення")
    parser.add_argument("--png", type=str, default="fib_lru_vs_splay.png", help="Куди зберегти графік")
    args = parser.parse_args()

    ns = list(range(0, args.nmax + 1, args.step))
    lru_times, splay_times = measure_times(ns, repeats=args.repeats)

    # Таблиця
    print_table(ns, lru_times, splay_times)

    # Графік
    plot_times(ns, lru_times, splay_times, args.png)
    print(f"\nГрафік збережено у: {args.png}")

if __name__ == "__main__":
    main()

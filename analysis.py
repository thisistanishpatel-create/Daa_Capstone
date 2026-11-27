"""Performance & complexity analysis of Huffman coding."""
import math
import random
import string
import time

from huffman import (build_frequency, build_tree, generate_codes, encode,
                     compress_bytes, decompress_bytes)


def entropy(freq):
    """Shannon entropy = theoretical minimum bits/char."""
    n = sum(freq.values())
    return -sum(f / n * math.log2(f / n) for f in freq.values())


def avg_code_length(freq, codes):
    n = sum(freq.values())
    return sum(freq[c] * len(codes[c]) for c in freq) / n


def print_code_table(freq, codes):
    print(f"{'Char':<8}{'Freq':>8}{'Code':>14}{'Bits':>6}")
    print("-" * 36)
    for ch in sorted(freq, key=lambda c: (len(codes[c]), codes[c])):
        shown = repr(ch)[1:-1] if ch.isprintable() and ch != " " else repr(ch)[1:-1] or ch
        if ch == " ":
            shown = "SPACE"
        print(f"{shown:<8}{freq[ch]:>8}{codes[ch]:>14}{len(codes[ch]):>6}")


def compression_report(text):
    blob, freq, codes, root = compress_bytes(text)
    original = len(text.encode("utf-8"))
    compressed = len(blob)
    ok = decompress_bytes(blob) == text
    print_code_table(freq, codes)
    print()
    print(f"Distinct characters (k)   : {len(freq)}")
    print(f"Original size             : {original} bytes")
    print(f"Compressed size           : {compressed} bytes (includes header)")
    print(f"Space saved               : {(1 - compressed / original) * 100:.2f} %")
    print(f"Compression ratio         : {original / compressed:.2f} : 1")
    print(f"Entropy (theoretical min) : {entropy(freq):.3f} bits/char")
    print(f"Huffman avg code length   : {avg_code_length(freq, codes):.3f} bits/char")
    print(f"Fixed length (ASCII)      : 8 bits/char")
    print(f"Lossless check (decode == original): {'PASS' if ok else 'FAIL'}")


def benchmark(sizes=(1_000, 10_000, 100_000, 500_000, 1_000_000)):
    """Time each phase for growing input sizes -> shows O(n) behaviour."""
    random.seed(42)
    alphabet = string.ascii_lowercase + " "
    weights = [random.randint(1, 20) for _ in alphabet]   # skewed like real text
    rows = []
    print(f"{'Size(chars)':>12}{'Freq(ms)':>10}{'Tree(ms)':>10}{'Encode(ms)':>12}"
          f"{'Orig(B)':>10}{'Comp(B)':>10}{'Saved%':>8}")
    for n in sizes:
        text = "".join(random.choices(alphabet, weights, k=n))
        t0 = time.perf_counter(); freq = build_frequency(text)
        t1 = time.perf_counter(); root = build_tree(freq)
        t2 = time.perf_counter(); codes = generate_codes(root); bits = encode(text, codes)
        t3 = time.perf_counter()
        blob, *_ = compress_bytes(text)
        assert decompress_bytes(blob) == text
        saved = (1 - len(blob) / n) * 100
        rows.append((n, (t1 - t0) * 1e3, (t2 - t1) * 1e3, (t3 - t2) * 1e3, n, len(blob), saved))
        print(f"{n:>12}{rows[-1][1]:>10.2f}{rows[-1][2]:>10.3f}{rows[-1][3]:>12.2f}"
              f"{n:>10}{len(blob):>10}{saved:>8.1f}")
    print("\nObservation: Frequency + Encode time grows ~linearly with n (O(n)).")
    print("Tree build time stays almost constant (depends only on k = 27 here).")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        ns = [r[0] for r in rows]
        fig, ax = plt.subplots(1, 2, figsize=(11, 4))
        ax[0].plot(ns, [r[1] + r[3] for r in rows], "o-", label="Frequency + Encode")
        ax[0].plot(ns, [r[2] for r in rows], "s-", label="Tree build")
        ax[0].set_xlabel("Input size (chars)"); ax[0].set_ylabel("Time (ms)")
        ax[0].set_title("Running time vs input size"); ax[0].legend(); ax[0].grid(alpha=.3)
        ax[1].bar([str(n) for n in ns], [r[4] for r in rows], label="Original")
        ax[1].bar([str(n) for n in ns], [r[5] for r in rows], label="Compressed")
        ax[1].set_xlabel("Input size (chars)"); ax[1].set_ylabel("Bytes")
        ax[1].set_title("Original vs Compressed size"); ax[1].legend()
        plt.tight_layout(); plt.savefig("benchmark.png", dpi=130)
        print("Graph saved as benchmark.png")
    except ImportError:
        print("(matplotlib not installed - graph skipped. pip install matplotlib)")

"""
Huffman Coding File Compressor - command line tool

Usage:
  python main.py demo                         # step-by-step demo on a small string
  python main.py compress   in.txt out.huf    # compress a text file
  python main.py decompress out.huf back.txt  # restore original
  python main.py analyze    in.txt            # code table + size/entropy report
  python main.py benchmark                    # time vs input size (+ graph)
"""
import os
import sys

from huffman import (build_frequency, build_tree, generate_codes, encode,
                     decode, compress_file, decompress_file)
import analysis


def print_tree(node, prefix="", is_left=None):
    """ASCII drawing of the Huffman tree."""
    if node is None:
        return
    label = (repr(node.char) if node.char != " " else "' '") if node.is_leaf() else "*"
    edge = "" if is_left is None else ("0--" if is_left else "1--")
    print(f"{prefix}{edge}[{label}:{node.freq}]")
    child_prefix = prefix + ("" if is_left is None else "    ")
    print_tree(node.left, child_prefix, True)
    print_tree(node.right, child_prefix, False)


def demo(text="abracadabra alakazam"):
    print(f"Input text: {text!r}\n")
    freq = build_frequency(text)
    print("STEP 1 - Frequencies:", dict(sorted(freq.items())), "\n")
    root = build_tree(freq)
    print("STEP 2 - Huffman Tree (0 = left, 1 = right):")
    print_tree(root)
    codes = generate_codes(root)
    print("\nSTEP 3 - Codes:")
    analysis.print_code_table(freq, codes)
    bits = encode(text, codes)
    print(f"\nSTEP 4 - Encoded bits ({len(bits)} bits vs {len(text) * 8} bits fixed):")
    print(bits)
    print("\nSTEP 5 - Decoded:", repr(decode(bits, root)))
    print("Match:", decode(bits, root) == text)


def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    cmd = sys.argv[1]
    if cmd == "demo":
        demo(*sys.argv[2:3])
    elif cmd == "compress" and len(sys.argv) == 4:
        freq, codes, root, o, c = compress_file(sys.argv[2], sys.argv[3])
        print(f"Compressed {sys.argv[2]} -> {sys.argv[3]}")
        print(f"Original: {o} bytes | Compressed: {c} bytes | Saved: {(1 - c / o) * 100:.2f}%")
    elif cmd == "decompress" and len(sys.argv) == 4:
        decompress_file(sys.argv[2], sys.argv[3])
        print(f"Restored -> {sys.argv[3]}")
    elif cmd == "analyze" and len(sys.argv) == 3:
        with open(sys.argv[2], "r", encoding="utf-8") as f:
            analysis.compression_report(f.read())
    elif cmd == "benchmark":
        analysis.benchmark()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()

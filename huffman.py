"""
Huffman Coding - core algorithm
================================
Steps:
1. Count frequency of every character
2. Put each character in a Min-Heap (priority queue) by frequency
3. Repeatedly remove 2 smallest nodes, merge into a parent node (freq = sum), push back
4. Last node left = root of the Huffman Tree
5. Walk the tree: left edge = '0', right edge = '1' -> code of each character
6. Encode text using these codes; decode by walking the tree bit by bit

Time complexity : O(n + k log k)   n = text length, k = distinct characters
Space complexity: O(k)             tree + code table (plus O(n) for output)
"""
import heapq
import struct
from collections import Counter

MAGIC = b"HUF1"


class Node:
    """A node of the Huffman Tree."""
    __slots__ = ("char", "freq", "left", "right", "order")

    def __init__(self, char, freq, left=None, right=None, order=0):
        self.char = char      # None for internal nodes
        self.freq = freq
        self.left = left
        self.right = right
        self.order = order    # tie-breaker so same results every run

    def __lt__(self, other):  # needed by heapq
        return (self.freq, self.order) < (other.freq, other.order)

    def is_leaf(self):
        return self.left is None and self.right is None


# ---------- Step 1 ----------
def build_frequency(text):
    """Character -> frequency. O(n)"""
    return dict(Counter(text))


# ---------- Step 2-4 ----------
def build_tree(freq):
    """Build Huffman Tree with a min-heap. O(k log k)"""
    if not freq:
        return None
    heap, counter = [], 0
    for ch, f in sorted(freq.items()):          # sorted -> deterministic
        heap.append(Node(ch, f, order=counter))
        counter += 1
    heapq.heapify(heap)
    while len(heap) > 1:
        a = heapq.heappop(heap)                  # smallest
        b = heapq.heappop(heap)                  # second smallest
        heapq.heappush(heap, Node(None, a.freq + b.freq, a, b, counter))
        counter += 1
    return heap[0]


# ---------- Step 5 ----------
def generate_codes(root):
    """Walk the tree to get binary code of each char. O(k)"""
    if root is None:
        return {}
    if root.is_leaf():                           # only one distinct char
        return {root.char: "0"}
    codes = {}
    stack = [(root, "")]                         # iterative DFS (no recursion limit)
    while stack:
        node, path = stack.pop()
        if node.is_leaf():
            codes[node.char] = path
        else:
            stack.append((node.right, path + "1"))
            stack.append((node.left, path + "0"))
    return codes


# ---------- Step 6 ----------
def encode(text, codes):
    """Text -> string of '0'/'1'. O(n)"""
    return "".join(codes[ch] for ch in text)


def decode(bits, root):
    """Bit string -> original text by walking the tree. O(length of bits)"""
    if root is None:
        return ""
    if root.is_leaf():                           # single-char file
        return root.char * len(bits)
    out, node = [], root
    for b in bits:
        node = node.left if b == "0" else node.right
        if node.is_leaf():
            out.append(node.char)
            node = root
    return "".join(out)


# ---------- bit packing ----------
def bits_to_bytes(bits):
    """'0101...' -> bytes. Returns (data, padding) padding = extra 0s added."""
    padding = (8 - len(bits) % 8) % 8
    bits += "0" * padding
    data = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8))
    return data, padding


def bytes_to_bits(data, padding):
    bits = "".join(f"{b:08b}" for b in data)
    return bits[:len(bits) - padding] if padding else bits


# ---------- file level ----------
# File format:  MAGIC(4) | header_len(4) | header(freq table) | padding(1) | data
def pack_freq(freq):
    """Compact binary frequency table: count(4) then [char code(4) + freq(4)] each."""
    out = struct.pack(">I", len(freq))
    for ch, f in freq.items():
        out += struct.pack(">II", ord(ch), f)
    return out


def unpack_freq(data):
    n = struct.unpack(">I", data[:4])[0]
    freq = {}
    for i in range(n):
        cp, f = struct.unpack(">II", data[4 + 8 * i: 12 + 8 * i])
        freq[chr(cp)] = f
    return freq


def compress_bytes(text):
    freq = build_frequency(text)
    root = build_tree(freq)
    codes = generate_codes(root)
    bits = encode(text, codes)
    data, padding = bits_to_bytes(bits)
    header = pack_freq(freq)
    blob = MAGIC + struct.pack(">I", len(header)) + header + bytes([padding]) + data
    return blob, freq, codes, root


def decompress_bytes(blob):
    if blob[:4] != MAGIC:
        raise ValueError("Not a valid Huffman compressed file")
    hlen = struct.unpack(">I", blob[4:8])[0]
    freq = unpack_freq(blob[8:8 + hlen])
    padding = blob[8 + hlen]
    data = blob[9 + hlen:]
    root = build_tree(freq)                      # rebuild SAME tree from frequencies
    if root is not None and root.is_leaf():
        return root.char * root.freq
    return decode(bytes_to_bits(data, padding), root)


def compress_file(src, dst):
    with open(src, "r", encoding="utf-8") as f:
        text = f.read()
    blob, freq, codes, root = compress_bytes(text)
    with open(dst, "wb") as f:
        f.write(blob)
    return freq, codes, root, len(text.encode("utf-8")), len(blob)


def decompress_file(src, dst):
    with open(src, "rb") as f:
        blob = f.read()
    text = decompress_bytes(blob)
    with open(dst, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    return text

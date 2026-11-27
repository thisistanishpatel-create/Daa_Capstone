# Viva Notes - Huffman Coding (Hinglish)

## 1. 30 second explanation (ye pehle bol dena)
"Ma'am, mera project Huffman Coding hai. Normal text me har character 8 bit leta hai. Maine ye idea use kiya ki
jo character zyada baar aata hai usko chhota code do, aur jo kam aata hai usko bada code. Iske liye pehle frequency
count ki, phir min-heap se Huffman tree banaya, tree se binary codes nikale, file encode ki aur decode karke
verify kiya ki original file wapas mil jaye. Ye ek **Greedy algorithm** hai, aur complexity **O(n + k log k)** hai."

## 2. Algorithm kaise kaam karta hai (example: "aaabbc")
* Frequency: a=3, b=2, c=1
* Sabse chhote 2 lo: c(1) + b(2) -> naya node(3)
* Ab nodes: a(3), node(3) -> merge -> root(6)
* Codes: a = 0, b = 10, c = 11 (frequent `a` ko 1 bit mila)
* "aaabbc" = 000 10 10 11 -> 9 bit, jabki fixed 8 bit/char me 48 bit lagte.

## 3. Important questions aur answers
**Q. Huffman Greedy kyu hai?**
Har step pe hum locally best choice lete hain - 2 sabse kam frequency wale nodes merge. Ye choice kabhi wapas
nahi badalte, aur ye proved hai ki isse globally optimal code milta hai.

**Q. Prefix-free code kya hota hai? Kyu zaroori hai?**
Koi bhi code kisi dusre code ka starting part nahi hota. Characters sirf tree ke **leaf** pe hote hain, isliye
ye property automatically milti hai. Isse decoding me confusion nahi hoti (separator ki zaroorat nahi).

**Q. Time complexity?**
Frequency count O(n). n/k heap operations: har ek O(log k) -> tree O(k log k). Encode/decode O(n).
Total **O(n + k log k)**. k chhota hota hai (ASCII me max 128) isliye practically O(n).

**Q. Space complexity?**
Tree aur code table O(k). Output O(n).

**Q. Min-heap kyu use kiya? Sorted array kyu nahi?**
Har baar sabse chhote 2 nodes chahiye aur naya node wapas daalna hai. Heap me insert/extract O(log k) hai,
sorted array me insert O(k) padta.

**Q. Decoder ko tree kaise milta hai?**
Compressed file ke header me frequency table save hai. Decoder wahi frequencies se wahi tree dobara banata hai
(tie-break order fix hai isliye tree same banta hai).

**Q. Padding kyu hai?**
File bytes (8 bit) me likhi jaati hai, par bits ki length 8 ka multiple nahi hoti. Last byte me extra 0 add
karte hain aur 1 byte me padding count save karte hain taaki decode ke time hata sakein.

**Q. Compression kam kyu aaya chhoti file me?**
Header (frequency table) fixed jagah leta hai. Badi file me wo overhead chhota ho jata hai (hamare result: 10% vs 44%).

**Q. Kya Huffman hamesha compress karta hai?**
Nahi. Agar saare characters ki frequency lagbhag barabar ho (random data), to codes ~8 bit ke ho jate hain
aur header ki wajah se file bad bhi sakti hai.

**Q. Entropy kya hai? Aapne kyu nikali?**
Shannon entropy = theoretical minimum average bits/char. Hamara Huffman avg 4.382 hai aur entropy 4.352 -
yaani bahut optimal hai (entropy se bas thoda sa upar, hamesha >= entropy).

**Q. Edge cases?**
Empty file, file me sirf ek character (code "0" diya), unicode/Hindi/emoji, newline - sab unit tests me cover hain.

**Q. Limitation / improvement?**
Sirf text; header bada; **Canonical Huffman** se header chhota ho sakta hai; LZ77 + Huffman (DEFLATE/ZIP) aur
better compression deta hai.

**Q. Real life me kahan use hota hai?**
ZIP/GZIP (DEFLATE), PNG, JPEG, MP3.

**Q. Fixed-length vs Huffman?**
Fixed: har char 8 bit. Huffman variable-length: frequent = chhota code -> kam total bits.

## 4. Demo flow (viva me ye order me chalana)
1. `python main.py demo` -> tree aur codes dikhao
2. `python main.py analyze samples/sample_large.txt` -> size comparison
3. compress + decompress chalao, dikhao file same hai
4. `python main.py benchmark` -> graph dikhao (linear growth)
5. `python -m unittest discover -s tests -v` -> 11 tests pass

## 6. Website + project (combined) ke sawal
**Q. Website me Huffman kaise use hua?**
Website ke peeche Python server (`server.py`) chalta hai. "Download .huf" dabane par text `/api/compress` pe jata hai, server
`huffman.compress_bytes()` chalata hai (frequency, min-heap tree, codes, encode, bits pack) aur `.huf` file wapas bhejta hai.
Restore tab me `.huf` file `/api/restore` pe jati hai, server `huffman.decompress_bytes()` se original text wapas deta hai.
Tree, code table aur bits jo screen pe dikhte hain wo browser me wahi algorithm se draw hote hain.

**Q. Server na ho to?**
`web/index.html` seedha kholo, to wahi algorithm JavaScript me browser ke andar chalta hai. Page ke upar "Engine" likha dikhta hai.

**Q. Python aur JavaScript dono ki file compatible kaise hai?**
Dono same `HUF1` file format aur same tie-break use karte hain, isliye same tree banta hai. `sample_large.txt` ka output
dono me byte-for-byte same hai (15,363 bytes).

**Q. File kahin upload hoti hai?**
Server tumhare apne laptop (localhost) pe chalta hai, internet pe kuch nahi jata.

**Q. Server me kaunsa framework?**
Koi nahi. Python ka built-in `http.server` (standard library), kuch install nahi karna.

**Q. API kya hain?**
`GET /api/ping`, `POST /api/compress` (text se .huf), `POST /api/restore` (.huf se text). Galat file par HTTP 400 aur clear message.

**Q. Responsive kaise?**
CSS grid: bade screen pe 2 columns, 900px se chhote pe 1 column; tree/tables apne box me scroll hote hain.

**Q. Limitation?**
Sirf UTF-8 text files, 3 MB tak. Binary files ke liye byte-level version banana padega.

## 7. Demo order (viva me)
1. Terminal: `python server.py` (browser khud khulega). Upar "Engine: Python server" dikhao.
2. Sample text ka Result dikhao (32% saved, "Yes, lossless"). "ABRACADABRA" dabake tree dikhao, code row pe hover karo.
3. Koi text file choose karo, **Download .huf file** dabao.
4. Restore tab me wahi `.huf` daalo, **Download restored text** dabao, file same hai dikhao.
5. Terminal me `python main.py analyze samples/sample_large.txt` aur `python -m unittest discover -s tests -v` (16 tests OK).

# Numerical experiment specification

The raw text snapshots and ngram counts are in `sources/`; `data/provenance.json` records download URLs and SHA-256 hashes. The six texts were obtained from GITenberg mirrors because the Gutenberg web endpoints were unavailable during this run. The new census therefore supersedes all earlier manuscript numerical values.

The code removes text before the Gutenberg START delimiter and after the END delimiter, then retains ASCII A-Z/a-z characters and uppercases. Paragraph boundaries, word boundaries, punctuation and other characters disappear. It does not join different books. It does not otherwise remove prefaces or other material inside the delimiters. The resulting total is 2,791,233 letters.

`experiment.cpp` computes a deduplicated exact census for lengths 10-24. It packs each plaintext and its first-occurrence repetition pattern into unsigned 128-bit integers (5 bits per position, at most 120 bits). It uses exact sorting/equality on those integers, not probabilistic hashes.

Model sampling uses public monogram through quadgram tables, normalized row by row with no smoothing; empty rows fall back to the longest suffix with available counts. There are 23 empty quadgram-context rows and none at shorter orders. The four orders use respectively 0, 1, 2, 3 preceding letters, initialized with the corresponding lower-order transitions.

Five independent codebooks per model use seeds 202611190000 + 100*model_order + replicate_index (indices 0-4). At each length there are exactly M_N entries. Identical plaintext entries remain in the codebook and preserve their multiplicities. A pattern class contributes all its entries to success precisely when they all represent the same plaintext value. The estimate is therefore unbiased for the exact iid-codebook ensemble probability. Different lengths use prefixes of the same generated strings and are coupled; different replicates use independent seeded streams. Standard errors are based on variability across the five codebooks, not on treating all entries as independent Bernoulli observations.

The uniform-law curve uses the occupancy recurrence and `log1p` for powers. All census and simulation output CSVs are supplied. The plotted bands are ±2 estimated standard errors, not guaranteed confidence intervals and not model-error bands. Zero observed ambiguities are omitted from the logarithmic panel; they do not prove a zero population ambiguity rate.

Run `python3 reproduce.py --plots-only` to reproduce figures from supplied results. Run `python3 reproduce.py` to recompile and repeat census/simulations. Default execution uses the included snapshots and requires no network. Requirements: C++17 compiler, Python 3, NumPy, Matplotlib. The recorded run used g++ 14.2.0, Python 3.12.14, NumPy 2.3.5 and Matplotlib 3.10.8.

The public NGRAMS page describes its files as distributed under GNU LGPL. Its source URL is https://people.math.sc.edu/Burkardt/datasets/ngrams/ngrams.html . Raw Gutenberg texts retain their original header/footer attribution and distribution notices. Model-table source-corpus overlap with the six novels is unknown.

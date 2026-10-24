# Frozen structural format V2

Source: the user's explicit follow-up authorization, sections 5–8. No Gold, paper IDs, model calls, numeric cleaning or semantic correction in this parser.

1. Inherit the exact neutral prefix and paired complete code fences allowed by V1. Preserve a complete single array verbatim.
2. Merge complete self-contained TDMR arrays in encounter order. Retain each object's exact source substring, numbers, key order and duplicates; change only array containers and separators.
3. Multi-group external text is restricted to whitespace, the original neutral prefix and Markdown bold group labels equal to a uniform Task/Dataset/Metric value already present in every row of the following group. No field is supplied from headings. Unknown prose, revisions, alternatives and candidate-answer headings are rejected. This conservative lexical gate avoids guessing semantic relations.
4. Add one final `]` only for a single array whose nonempty final object is completely closed, with no trailing comma, incomplete value/string or other residue. Preserve the original length-stop status separately; this is not evidence of exhaustive extraction.
5. JSONDecoder with duplicate-key rejection handles strings and escapes. All rows must have exactly Task/Dataset/Metric/Result; first three are strings, Result is a finite string/int/float as in V1. Nested arrays, partial records, invalid fields, booleans/nonfinite numbers and unpaired fences fail. Never discard a tail to salvage partial predictions.
6. All42 responses receive the same rules. Freeze this file, parser and passing tests before scoring. Original40 must preserve row count/order/key values/duplicates and official str(Result).

Offsets are zero-based Python Unicode character offsets, half-open; SHA256 uses UTF-8. Actual generation stop reasons are recorded independently of syntax validity.

# Data Size Optimization Analysis

## Current State

| File | Size |
|------|------|
| `resistors_compact.json` | ~7.3 MB |
| `data.js` | ~9.0 MB |
| **Total loaded by browser** | **~9.0 MB** (data.js) |

## Data Structure

Each resistor record is a dict with 11 fields:
```json
{"p":"3","pn":"ERA3KEB2433V","s":"0","se":"18","pr":"5","sz":"4","rv":243000.0,"rt":"1","pk":"3","tc":"18","de":"4"}
```

The lookup tables (9 categories) are stored separately and referenced by integer index.

## Optimization Opportunities

### 1. Remove `de` (Datasheet) field from resistor records (BIGGEST WIN)

The `de` field is a lookup index into the `datasheet` lookup table. It's only used in the `openDatasheet()` function in `app.js`. If datasheet URLs are rarely used, we could:
- **Option A:** Remove `de` entirely from resistor records — saves ~1 byte per resistor × 79k = ~79 KB
- **Option B:** Keep `de` but only for resistors that actually have a datasheet URL (most might be empty/"nan")

**Estimated savings:** ~80 KB (minor)

### 2. Use arrays instead of objects for resistor records (BIGGEST WIN)

Currently each resistor is a dict with 11 key-value pairs. The keys are repeated 79,105 times:
```json
{"p":"3","pn":"ERA3KEB2433V","s":"0","se":"18","pr":"5","sz":"4","rv":243000.0,"rt":"1","pk":"3","tc":"18","de":"4"}
```

If we use a positional array with a header mapping, each resistor becomes:
```json
["3","ERA3KEB2433V","0","18","5","4",243000.0,"1","3","18","4"]
```

**Savings:** ~22 bytes per resistor (the key names `"p":` `"pn":` etc. repeated 79k times)
- **Estimated: ~1.7 MB savings** (from ~7.3 MB to ~5.6 MB)

### 3. Compress `pn` (Part Number) strings

Part numbers like `ERA3KEB2433V` are 11-15 chars each. If there are many similar prefixes, we could use a prefix table. However, part numbers are highly unique, so this won't help much.

### 4. Use `Int8Array` / typed arrays for numeric fields

Fields like `p`, `s`, `se`, `pr`, `sz`, `rt`, `pk`, `tc`, `de` are all small integers (0-30 range). We could store these as typed arrays in JavaScript, loaded as binary. But this requires significant frontend changes.

### 5. Gzip/Brotli compression on the server side

If the HTML is served via a web server, enabling gzip would reduce transfer size by ~70-80% (to ~2 MB). This is **zero code change** but requires server config.

### 6. Lazy-load the data

Split the data into chunks (e.g., by series or product category) and load on demand. This requires significant frontend refactoring.

## Recommended Approach

### Phase 1: Arrays instead of objects (BIGGEST WIN, minimal effort)

Change the resistor records from dicts to arrays, with a header mapping in the frontend.

**Changes needed:**

1. **In `compact_resistors_v2.py`** (or the pipeline within `extract_from_xlsm.py`):
   - Change `df.to_dict(orient='records')` to `df.values.tolist()`
   - Add a `columns` array to the output that maps column positions to field names

2. **In `app.js`**:
   - Add a column index mapping at the top:
     ```js
     const COL = { p: 0, pn: 1, s: 2, se: 3, pr: 4, sz: 5, rv: 6, rt: 7, pk: 8, tc: 9, de: 10 };
     ```
   - Replace all `r.p` with `r[COL.p]`, `r.pn` with `r[COL.pn]`, etc.

**Estimated result:**
- `resistors_compact.json`: ~7.3 MB → ~5.6 MB (**-23%**)
- `data.js`: ~9.0 MB → ~7.3 MB (**-19%**)

### Phase 2: Remove unused datasheet field (optional)

Check how many resistors actually have a datasheet URL. If most are empty, remove the `de` field from records that have no datasheet.

### Phase 3: Server-side compression (if applicable)

If you serve this via any web server, enable gzip/brotli. This is the single biggest impact with zero code changes.

## Summary

| Optimization | Effort | Savings | Risk |
|-------------|--------|---------|------|
| Arrays instead of objects | Medium (changes in both Python + JS) | ~1.7 MB (19-23%) | Low — mechanical refactor |
| Remove empty datasheets | Low | ~80 KB | Low |
| Server gzip | None (config only) | ~6-7 MB transfer | None |
| Typed arrays | High | ~3-4 MB | High — complex refactor |
| Lazy loading | High | Variable | High — architecture change |

**My recommendation:** Do Phase 1 (arrays) + Phase 3 (gzip if applicable). This gives the best effort-to-reward ratio.

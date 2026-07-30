# Plan: Slider Debounce (200ms)

## Overview

Debounce the resistance range slider input by 200ms to avoid expensive filtering/rendering on every slider tick.

---

## Change: Debounce Slider Input (200ms)

### Current Behavior

In [`app.js:51-52`](../app.js:51), both slider inputs fire `onRangeInput` directly on every `input` event:

```js
document.getElementById('resSliderMin').oninput = onRangeInput;
document.getElementById('resSliderMax').oninput = onRangeInput;
```

[`onRangeInput()`](../app.js:183) computes new resistance values, updates text inputs, updates the track UI, and calls `refresh()` which filters all resistors and re-renders the table. This happens on every single slider movement (potentially hundreds of events per drag).

### Implementation

1. Create a debounce utility function at the top of [`app.js`](../app.js):
   ```js
   function debounce(fn, delay) {
       let timer;
       return function(...args) {
           clearTimeout(timer);
           timer = setTimeout(() => fn.apply(this, args), delay);
       };
   }
   ```

2. Wrap `onRangeInput` with a 200ms debounce:
   ```js
   const onRangeInputDebounced = debounce(onRangeInput, 200);
   ```

3. Update the event listeners in `initApp()` to use the debounced version:
   ```js
   document.getElementById('resSliderMin').oninput = onRangeInputDebounced;
   document.getElementById('resSliderMax').oninput = onRangeInputDebounced;
   ```

### Why this approach
- Simple, no external dependencies
- The debounced function preserves `this` and arguments
- The track visual update and text field updates will also be debounced, which is fine since they're derived from the same computation

---

## Files to Modify

| File | Changes |
|------|---------|
| [`app.js`](../app.js) | 1. Add `debounce()` utility function<br>2. Create debounced `onRangeInput` wrapper<br>3. Update slider event listeners in `initApp()` |

## Testing Checklist

- [ ] Drag slider — filtering/rendering should only fire after 200ms of no slider movement
- [ ] Drag slider rapidly — only the last position should trigger a refresh

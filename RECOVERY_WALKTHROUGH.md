# Conflict Recovery Walkthrough

## 1. Problem Identification
The repository was in a critical state following several failed integration attempts:
- **`main` Branch Corruption**: The `main` branch contained raw git conflict markers in `checkout.js`, making the codebase unrunnable.
- **WIP Commits**: Feature branches were merged with unresolved conflicts and "Work In Progress" commit messages.
- **Duplicate History**: A rounding fix was cherry-picked onto `main` while also existing in feature branches, causing diverged history.
- **Divergent Feature Logic**: Two major features (`discounts` and `tax-v2`) were developed in isolation and collided in the same logic block.

## 2. Recovery Strategy: The "Clean Rebuild"
Instead of trying to patch the broken `main`, I used a reconstruction approach:
1. **Reset to Last Known Good State**: I identified the last stable commit before the messy merges.
2. **Isolation**: Created a dedicated `recovery/stable-release` branch to work safely.
3. **Sequential Integration**: 
   - Integrated the `discounts` feature first.
   - Resolved conflicts manually to ensure the `rounding-fix` (already on main) was preserved.
   - Integrated the `tax-v2` feature second.
   - Combined all three logics (Discount -> Tax -> Rounding) into a single functional pipeline.

## 3. Implementation Details
The core logic in `checkout.js` was restored to:
```javascript
function checkout(items) {
    let total = items.reduce(...);
    total = total * 0.9; // 10% Discount
    total = total * 1.05; // 5% Tax
    return Math.round(total * 100) / 100; // Final Rounding
}
```

## 4. Validation Evidence
A validation script `test.js` was created to verify the business logic.
**Test Case**: 
- Input: \$10.00 apple.
- Expected: \$9.45 (\$10.00 - 10% = \$9.00; \$9.00 + 5% = \$9.45).
- Result: **SUCCESS**.

## 5. Final Repository State
- Clean, linear history for features.
- Descriptive commit messages.
- No conflict markers.
- Ready for production deployment.

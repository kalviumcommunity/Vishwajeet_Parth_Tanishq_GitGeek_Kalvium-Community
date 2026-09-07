# Repository Investigation Report

## 1. Identified Issues
- **Raw Conflict Markers in Main**: Commit `0565dcf` (merged from `integration`) contains git conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`) in `checkout.js`. This will cause the application to crash in production.
- **Unfinished Work Merged**: The commit `d050dd7` on `feature/discounts` was committed with unresolved conflicts and a "WIP" message.
- **Duplicate Logic**: The "rounding fix" was cherry-picked onto `main` but also exists in the feature branch history, leading to potential merge headaches later.
- **Diverged Features**: `feature/tax-v2` and `feature/discounts` both modified the same lines in `checkout.js` without a proper integration strategy.

## 2. Workflow Failures
- **Commiting Conflicts**: Developers committed files with conflict markers instead of resolving them.
- **Poor Integration Testing**: Merges were pushed to `main` without verifying that the code actually runs.
- **Fragmented Fixes**: Cherry-picking fixes to `main` instead of merging/rebasing properly created duplicate commits.

## 3. Recovery Plan
1. **Branch Isolation**: Create `recovery/fix-stable`.
2. **Clean Integration**:
    - Rebase `feature/discounts` onto `main` (before the mess).
    - Rebase `feature/tax-v2` onto the new state.
    - Ensure `bugfix/rounding` is integrated exactly once.
3. **Conflict Resolution**: Combine the logic:
    ```javascript
    let total = items.reduce(...);
    total = total * 0.9; // Discount
    total = total * 1.05; // Tax
    return Math.round(total * 100) / 100; // Rounding
    ```
4. **Validation**: Run a test script to ensure $10.00 -> $9.00 -> $9.45.
5. **Main Reset**: Force update `main` to the recovered state.

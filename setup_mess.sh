#!/bin/bash
# setup_mess.sh
# This script simulates a messy git history in the current directory.

# 1. Base Files
cat <<EOF > checkout.js
function checkout(items) {
    console.log("Starting checkout...");
    let total = items.reduce((sum, item) => sum + item.price, 0);
    return total;
}
module.exports = checkout;
EOF

cat <<EOF > inventory.js
const inventory = {
    "apple": 1.0,
    "banana": 0.5,
    "orange": 0.8
};
module.exports = inventory;
EOF

git add .
git commit -m "feat: initial checkout and inventory system"

# 2. Diverge: feature/discounts
git checkout -b feature/discounts
cat <<EOF > checkout.js
function checkout(items) {
    console.log("Starting checkout with discounts...");
    let total = items.reduce((sum, item) => sum + item.price, 0);
    // Apply 10% discount
    total = total * 0.9;
    return total;
}
module.exports = checkout;
EOF
git add checkout.js
git commit -m "feat: implement 10% global discount"

# 3. Diverge: feature/tax-v2 (Conflicts with discounts)
git checkout main
git checkout -b feature/tax-v2
cat <<EOF > checkout.js
function checkout(items) {
    console.log("Starting checkout with tax...");
    let total = items.reduce((sum, item) => sum + item.price, 0);
    // Apply 5% tax
    total = total * 1.05;
    return total;
}
module.exports = checkout;
EOF
git add checkout.js
git commit -m "feat: implement 5% tax calculation"

# 4. Diverge: bugfix/rounding
git checkout main
git checkout -b bugfix/rounding
cat <<EOF > checkout.js
function checkout(items) {
    console.log("Starting checkout...");
    let total = items.reduce((sum, item) => sum + item.price, 0);
    // Fix rounding issue
    return Math.round(total * 100) / 100;
}
module.exports = checkout;
EOF
git add checkout.js
git commit -m "fix: resolve floating point rounding error"

# 5. The "Dirty Merge"
git checkout feature/discounts
git merge bugfix/rounding -m "merge fix into discounts"

# 6. Another "Dirty Merge" (with manual conflict mess)
git merge feature/tax-v2 -m "trying to merge tax" || true
# Leave conflict markers in the file but commit it anyway (BAD PRACTICE)
cat <<EOF > checkout.js
function checkout(items) {
<<<<<<< HEAD
    console.log("Starting checkout with discounts...");
    let total = items.reduce((sum, item) => sum + item.price, 0);
    // Apply 10% discount
    total = total * 0.9;
=======
    console.log("Starting checkout with tax...");
    let total = items.reduce((sum, item) => sum + item.price, 0);
    // Apply 5% tax
    total = total * 1.05;
>>>>>>> feature/tax-v2
    // Fix rounding issue
    return Math.round(total * 100) / 100;
}
module.exports = checkout;
EOF
git add checkout.js
git commit -m "fix conflicts partially - WIP"

# 7. Duplicate Commits on Main
git checkout main
git cherry-pick bugfix/rounding
echo "console.log('Production ready?');" >> api.js
git add api.js
git commit -m "chore: prepare for production"

# 8. Unstable Integration
git checkout -b integration
git merge feature/discounts -m "unstable merge of feature/discounts"
# Now integration branch has conflict markers from feature/discounts
git checkout main
git merge integration -m "deploying integration to main"
# Main is now broken.

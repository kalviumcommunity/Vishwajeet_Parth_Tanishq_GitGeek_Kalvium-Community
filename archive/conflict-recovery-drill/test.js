const checkout = require('./checkout');

const items = [
    { name: 'apple', price: 10.00 }
];

const total = checkout(items);
console.log(`Final Total: $${total}`);

if (total === 9.45) {
    console.log("SUCCESS: Calculation is correct.");
} else {
    console.log(`FAILURE: Expected $9.45 but got $${total}`);
    process.exit(1);
}

// Show form for either transaction or budget
function showForm(type){
    const container = document.getElementById("form-container");
    container.innerHTML = '';
    if(type === 'transaction'){
        container.innerHTML = `
        <h3>Add Transaction</h3>
        <form method="POST" action="/add_transaction">
            <select name="type">
                <option value="Income">Income</option>
                <option value="Expense">Expense</option>
            </select>
            <input type="text" name="category" placeholder="Category" required>
            <input type="number" step="0.01" name="amount" placeholder="Amount" required>
            <input type="text" name="description" placeholder="Description" required>
            <button type="submit">Add</button>
        </form>`;
    } else if(type === 'budget'){
        container.innerHTML = `
        <h3>Set Budget</h3>
        <form method="POST" action="/set_budget">
            <input type="text" name="category" placeholder="Category" required>
            <input type="number" step="0.01" name="budget" placeholder="Budget Amount" required>
            <button type="submit">Set Budget</button>
        </form>`;
    }
}

// Optional: Confirm before deleting a transaction
function confirmDelete() {
    return confirm("Are you sure you want to delete this transaction?");
}

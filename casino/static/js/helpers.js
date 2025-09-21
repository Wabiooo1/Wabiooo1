async function apiPost(path, data) {
    const res = await fetch(path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    return res.json();
}

async function apiGet(path) {
    const res = await fetch(path);
    return res.json();
}

function updateHeaderBalance(newBalance) {
    const el = document.getElementById('top-balance'); // ID correcto de layout.html
    if (el) el.textContent = newBalance.toFixed(2);
}
var apiKey = ""
var apiSecret = ""
const datetimeFormat = {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
}

function showToast(title, message) {
    var toastElement = document.getElementById('toast');
    var toast = new bootstrap.Toast(toastElement);
    toast.show();
    document.getElementById('toast-title').innerText = title;
    document.getElementById('toast-message').innerText = message;
}

function fetchAndUpdateUserProfile() {
    fetch('/api/user/profile', {
      method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
      updateApiKey(data.api_key, data.api_secret);
    })
    .catch(error => {
      showToast('Failed to fetch user profile', error);
    });
}

function fetchAndUpdateRecentPositions() {
    const spinner = document.getElementById("update-spinner");
    spinner.classList.remove("d-none");

    fetch('/api/master-traders/recent-positions', {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        updateRecentPositionsTable(data);
    })
    .catch(error => {
        showToast("Failed to fetch recent positions", error);
    })
    .finally(() => {
        spinner.classList.add('d-none');
    });
}

function fetchAndUpdateUserPositions() {
    const spinner = document.getElementById("user-pos-spinner");
    spinner.classList.remove("d-none");

    fetch('/api/user/positions', {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        updateUserPositionsTable(data);
    })
    .catch(error => {
        showToast("Failed to fetch user positions", error);
    })
    .finally(() => {
        spinner.classList.add('d-none');
    });
}

function updateRecentPositionsTable(positions) {
    var tableBody = document.getElementById('recent-positions').getElementsByTagName('tbody')[0];

    if (positions.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="7">No data</td></tr>';
    } else {
        tableBody.innerHTML = '';
    }

    positions.forEach(function(position) {
        var row = document.createElement('tr');
        row.classList.add("align-middle");
        const isBuy = position.side == "Buy";

        if (isBuy) {
            row.innerHTML += '<td><i class="bi bi-caret-up-fill" style="color: green"></i> ' + position.symbol + '</td>';
        } else {
            row.innerHTML += '<td><i class="bi bi-caret-down-fill" style="color: red"></i> ' + position.symbol + '</td>';
        }

        row.innerHTML += '<td>' + truncate(position.creator) + '</td>';
        row.innerHTML += '<td>' + position.entry_price + '</td>';
        row.innerHTML += '<td>' + position.size + '</td>';
        row.innerHTML += '<td>' + position.leverage + '</td>';

        const openAt = new Date(`${position.open_at}Z`);
        const formattedOpenAt = openAt.toLocaleString('ru-RU', datetimeFormat);
        row.innerHTML += '<td>' + formattedOpenAt + '</td>';

        var actionCell = document.createElement('td');
        var copyButton = document.createElement('button');
        copyButton.className = 'btn btn-primary btn-sm';
        copyButton.innerText = 'Copy';
        copyButton.onclick = () => {
            var modalElement = document.getElementById("copy-modal");
            var modal = new bootstrap.Modal(modalElement);
            modal.show();

            document.getElementById("symbol").innerText = position.symbol;
            const buyRadio = document.getElementById("buy");
            const sellRadio = document.getElementById("sell");
            buyRadio.checked = isBuy;
            sellRadio.checked = !isBuy;
        };
        actionCell.appendChild(copyButton);

        row.appendChild(actionCell);

        tableBody.appendChild(row);
    });

    var lastUpdated = document.getElementById('last-updated');
    var updatedAt = new Date().toLocaleString('ru-RU', datetimeFormat);
    lastUpdated.innerText = `Last updated: ${updatedAt}`;
}

function updateUserPositionsTable(positions) {
    var tableBody = document.getElementById('user-positions').getElementsByTagName('tbody')[0];

    if (positions.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="7">No data</td></tr>';
    } else {
        tableBody.innerHTML = '';
    }

    positions.forEach(function(position) {
        var row = document.createElement('tr');
        row.classList.add("align-middle");
        const isBuy = position.side == "Buy";

        if (isBuy) {
            row.innerHTML += '<td><i class="bi bi-caret-up-fill" style="color: green"></i> ' + position.symbol + '</td>';
        } else {
            row.innerHTML += '<td><i class="bi bi-caret-down-fill" style="color: red"></i> ' + position.symbol + '</td>';
        }

        row.innerHTML += '<td>' + position.avg_price + '</td>';
        row.innerHTML += '<td>' + position.mark_price + '</td>';
        row.innerHTML += '<td>' + position.size + '</td>';
        row.innerHTML += '<td>' + position.leverage + '</td>';
        row.innerHTML += '<td>' + position.unrealised_pnl + '</td>';

        var actionCell = document.createElement('td');
        var closeButton = document.createElement('button');
        closeButton.className = 'btn btn-danger btn-sm';
        closeButton.innerText = 'Close';
        closeButton.onclick = () => {
            closeButton.setAttribute('disabled', true);
            var csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value;
            fetch(`/api/user/positions/close?symbol=${position.symbol}&side=${position.side}`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                },
            })
            .then(response => response.json())
            .then(data => {
                fetchAndUpdateUserPositions();
            })
            .catch(error => {
                closeButton.removeAttribute('disabled');
                showToast("Failed to close position", error);
            })
            .finally(() => {

            });
        };
        actionCell.appendChild(closeButton);
        row.appendChild(actionCell);

        tableBody.appendChild(row);
    });

    var lastUpdated = document.getElementById('user-pos-last-updated');
    var updatedAt = new Date().toLocaleString('ru-RU', datetimeFormat);
    lastUpdated.innerText = `Last updated: ${updatedAt}`;
}

function truncate(string) {
    if (string.length > 10) {
        return string.substring(0, 10) + "...";
    } else {
        return string;
    }
}

function updateApiKey(newApiKey, newApiSecret) {
    const apiKeyElement = document.getElementById('apikey');
    const noApiKey = document.getElementById('no-apikey');
    const userPositionsTable = document.getElementById('user-positions');
    const addApiKey = document.getElementById('add-apikey');
    const editApiKey = document.getElementById('edit-apikey');
    apiKeyElement.innerHTML = truncate(newApiKey);
    if (newApiKey === "") {
        userPositionsTable.classList.add("d-none");
        noApiKey.classList.remove("d-none");
        addApiKey.classList.remove("d-none");
        editApiKey.classList.add("d-none");
    } else {
        userPositionsTable.classList.remove("d-none");
        noApiKey.classList.add("d-none");
        addApiKey.classList.add("d-none");
        editApiKey.classList.remove("d-none");
    }

    const apiKeyInput = document.getElementById("api-key");
    const apiSecretInput = document.getElementById("api-secret");
    apiKeyInput.value = newApiKey;
    apiSecretInput.value = newApiSecret;

    apiKey = newApiKey;
    apiSecret = newApiSecret;
}

fetchAndUpdateUserPositions();
fetchAndUpdateRecentPositions();
fetchAndUpdateUserProfile();

setInterval(fetchAndUpdateRecentPositions, 120000);
setInterval(fetchAndUpdateUserPositions, 60000);

document.getElementById('add-apikey').addEventListener('click', function() {
    updateApiKey(apiKey, apiSecret);
});

document.getElementById('edit-apikey').addEventListener('click', function() {
    updateApiKey(apiKey, apiSecret);
});

document.getElementById('submit-key').addEventListener('click', function() {
    var csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    var newApiKey = document.getElementById('api-key').value;
    var newApiSecret = document.getElementById('api-secret').value;

    const formData = new FormData();
    formData.append('key', newApiKey)
    formData.append('secret', newApiSecret)

    fetch('/api/user/profile', {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken,
      },
      body: formData,
    })
    .then(response => response.json())
    .then(data => {
        var modalElement = document.getElementById('apikey-modal');
        var modal = bootstrap.Modal.getInstance(modalElement);
        modal.hide();
        updateApiKey(newApiKey, newApiSecret);
    })
    .catch(error => {
      showToast("Failed to update API key", error);
    });
})

document.getElementById('copy-position').addEventListener('click', function() {
    this.setAttribute('disabled', true);
    document.getElementById('close-copy-modal').setAttribute('disabled', true);
    document.getElementById("copy-spinner").classList.remove('d-none');

    const symbol = document.getElementById("symbol").innerText;
    const side = document.getElementById("buy").checked ? "Buy" : "Sell";
    const cost = document.getElementById("cost").value;
    const leverage = document.getElementById("leverage").value;

    const formData = new FormData();
    formData.append('symbol', symbol);
    formData.append('side', side);
    formData.append('cost', cost);
    formData.append('leverage', leverage);

    var csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    fetch('/api/user/orders', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
        },
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        var modalElement = document.getElementById('copy-modal');
        var modal = bootstrap.Modal.getInstance(modalElement);
        modal.hide();

        fetchAndUpdateUserPositions();
    })
    .catch(error => {
        showToast("Failed to open position", error);
    })
    .finally(() => {
        this.removeAttribute('disabled');
        document.getElementById('close-copy-modal').removeAttribute('disabled');
        document.getElementById("copy-spinner").classList.add('d-none');
    });
});
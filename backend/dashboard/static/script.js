var apiKey = ""
var apiSecret = ""

const datetimeFormat = {
	day: "2-digit",
	month: "2-digit",
	year: "numeric",
	hour: "2-digit",
	minute: "2-digit",
}

function showToast(title, message) {
	var toastElement = document.getElementById("toast");
	var toast = new bootstrap.Toast(toastElement);
	toast.show();

	document.getElementById("toast-title").innerText = title;
	document.getElementById("toast-message").innerText = message;
}

function checkJsonResponse(response) {
    if (response.status === "error")
	    throw new Error(response.message);
    return response;
}

function fetchAndUpdateUserProfile() {
	fetch("/api/user/profile", {
			method: "GET"
		})
		.then(response => response.json())
		.then(data => checkJsonResponse(data))
		.then(data => {
			updateApiKey(data.api_key, data.api_secret);
		})
		.catch(error => {
			showToast("Failed to fetch user profile", error);
		});
}

function fetchAndUpdateRecentPositions() {
	const spinner = document.getElementById("recent-pos-spinner");
	spinner.classList.remove("d-none");

	fetch("/api/master-traders/recent-positions", {
			method: "GET"
		})
		.then(response => response.json())
		.then(data => checkJsonResponse(data))
		.then(data => {
			updateRecentPositionsTable(data);
		})
		.catch(error => {
			showToast("Failed to fetch recent positions", error);
		})
		.finally(() => {
			spinner.classList.add("d-none");
		});
}

function fetchAndUpdateUserPositions() {
	if (apiKey === "")
		return;

	const spinner = document.getElementById("user-pos-spinner");
	spinner.classList.remove("d-none");

	fetch("/api/user/positions", {
			method: "GET"
		})
		.then(response => response.json())
		.then(data => checkJsonResponse(data))
		.then(data => {
			updateUserPositionsTable(data);
		})
		.catch(error => {
			showToast("Failed to fetch user positions", error);
		})
		.finally(() => {
			spinner.classList.add("d-none");
		});
}

function updateRecentPositionsTable(positions) {
	var tableBody = document.getElementById("recent-positions").getElementsByTagName("tbody")[0];

	if (positions.length === 0) {
		tableBody.innerHTML = '<tr><td colspan="7">No data</td></tr>';
	} else {
		tableBody.innerHTML = '';
	}

	positions.forEach(function(position) {
		var row = document.createElement("tr");
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
		const formattedOpenAt = openAt.toLocaleString(datetimeFormat);
		row.innerHTML += '<td>' + formattedOpenAt + '</td>';

		var actionCell = document.createElement("td");
		var copyButton = document.createElement("button");
		copyButton.className = "btn btn-primary btn-sm";
		copyButton.innerText = "Copy";
		copyButton.onclick = () => {
			var modalElement = document.getElementById("copy-modal");
			var modal = new bootstrap.Modal(modalElement);
			modal.show();

			document.getElementById("symbol-label").innerText = position.symbol;
			const buyRadio = document.getElementById("buy-radio");
			const sellRadio = document.getElementById("sell-radio");
			buyRadio.checked = isBuy;
			sellRadio.checked = !isBuy;
		};

		actionCell.appendChild(copyButton);
		row.appendChild(actionCell);
		tableBody.appendChild(row);
	});

	var lastUpdated = document.getElementById("recent-pos-last-updated");
	var updatedAt = new Date().toLocaleString(datetimeFormat);
	lastUpdated.innerText = `Last updated: ${updatedAt}`;
}

function updateUserPositionsTable(positions) {
	var tableBody = document.getElementById("user-positions").getElementsByTagName("tbody")[0];

	if (positions.length === 0) {
		tableBody.innerHTML = '<tr><td colspan="7">No data</td></tr>';
	} else {
		tableBody.innerHTML = '';
	}

	positions.forEach(function(position) {
		var row = document.createElement("tr");
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
		if (position.unrealised_pnl >= 0)
		    row.innerHTML += '<td><span class="badge bg-success rounded-pill p-2">+' + position.unrealised_pnl + ' $</span></td>';
		else
		    row.innerHTML += '<td><span class="badge bg-danger rounded-pill p-2">' + position.unrealised_pnl + ' $</span></td>';

		var actionCell = document.createElement("td");
		var closeButton = document.createElement("button");
		closeButton.className = "btn btn-outline-danger btn-sm";
		closeButton.innerText = "Close";
		closeButton.onclick = () => {
			closeButton.setAttribute("disabled", true);
			var csrfToken = document.getElementsByName("csrfmiddlewaretoken")[0].value;
			fetch(`/api/user/positions/close?symbol=${position.symbol}&side=${position.side}`, {
					method: "POST",
					headers: {
						"X-CSRFToken": csrfToken,
					},
				})
				.then(response => response.json())
				.then(data => checkJsonResponse(data))
				.then(data => {
					fetchAndUpdateUserPositions();
				})
				.catch(error => {
					closeButton.removeAttribute("disabled");
					showToast("Failed to close position", error);
				})
		};

		actionCell.appendChild(closeButton);
		row.appendChild(actionCell);
		tableBody.appendChild(row);
	});

	var lastUpdated = document.getElementById("user-pos-last-updated");
	var updatedAt = new Date().toLocaleString(datetimeFormat);
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
    const updateUserPositions = newApiKey !== apiKey;
	const apiKeyElement = document.getElementById("api-key-label");
	const noApiKey = document.getElementById("no-api-key-alert");
	const userPositionsTable = document.getElementById("user-positions");
	const lastUpdated = document.getElementById("user-pos-last-updated");
	const addApiKey = document.getElementById("add-api-key-btn");
	const editApiKey = document.getElementById("edit-api-key-btn");

	if (newApiKey === "") {
		userPositionsTable.classList.add("d-none");
		lastUpdated.classList.add("d-none");
		noApiKey.classList.remove("d-none");
		addApiKey.classList.remove("d-none");
		editApiKey.classList.add("d-none");
	} else {
		userPositionsTable.classList.remove("d-none");
		lastUpdated.classList.remove("d-none");
		noApiKey.classList.add("d-none");
		addApiKey.classList.add("d-none");
		editApiKey.classList.remove("d-none");
	}

	const apiKeyInput = document.getElementById("api-key-input");
	const apiSecretInput = document.getElementById("api-secret-input");
	apiKeyInput.value = newApiKey;
	apiSecretInput.value = newApiSecret;
	apiKeyElement.innerHTML = truncate(newApiKey);

	apiKey = newApiKey;
	apiSecret = newApiSecret;

	if (updateUserPositions)
	    fetchAndUpdateUserPositions();
}

fetchAndUpdateUserProfile();
fetchAndUpdateRecentPositions();

setInterval(fetchAndUpdateRecentPositions, 120000);
setInterval(fetchAndUpdateUserPositions, 60000);

document.getElementById("add-api-key-btn").addEventListener("click", function() {
	updateApiKey(apiKey, apiSecret);
});

document.getElementById("edit-api-key-btn").addEventListener("click", function() {
	updateApiKey(apiKey, apiSecret);
});

document.getElementById("submit-api-key-btn").addEventListener("click", function() {
	var csrfToken = document.getElementsByName("csrfmiddlewaretoken")[0].value;
	var newApiKey = document.getElementById("api-key-input").value;
	var newApiSecret = document.getElementById("api-secret-input").value;

	const formData = new FormData();
	formData.append("key", newApiKey)
	formData.append("secret", newApiSecret)

	fetch("/api/user/profile", {
			method: "POST",
			headers: {
				"X-CSRFToken": csrfToken,
			},
			body: formData,
		})
		.then(response => response.json())
		.then(data => checkJsonResponse(data))
		.then(data => {
			var modalElement = document.getElementById("api-key-modal");
			var modal = bootstrap.Modal.getInstance(modalElement);
			modal.hide();
			updateApiKey(newApiKey, newApiSecret);
		})
		.catch(error => {
			showToast("Failed to update API key", error);
		});
})

document.getElementById("copy-position-btn").addEventListener("click", function() {
	this.setAttribute("disabled", true);
	document.getElementById("close-copy-modal").setAttribute("disabled", true);
	document.getElementById("copy-spinner").classList.remove("d-none");

	const symbol = document.getElementById("symbol-label").innerText;
	const side = document.getElementById("buy-radio").checked ? "Buy" : "Sell";
	const cost = document.getElementById("cost-input").value;
	const leverage = document.getElementById("leverage-input").value;

	const formData = new FormData();
	formData.append("symbol", symbol);
	formData.append("side", side);
	formData.append("cost", cost);
	formData.append("leverage", leverage);

	var csrfToken = document.getElementsByName("csrfmiddlewaretoken")[0].value;
	fetch("/api/user/orders", {
			method: "POST",
			headers: {
				"X-CSRFToken": csrfToken,
			},
			body: formData,
		})
		.then(response => response.json())
		.then(data => checkJsonResponse(data))
		.then(data => {
			var modalElement = document.getElementById("copy-modal");
			var modal = bootstrap.Modal.getInstance(modalElement);
			modal.hide();

			fetchAndUpdateUserPositions();
		})
		.catch(error => {
			showToast("Failed to open position", error);
		})
		.finally(() => {
			this.removeAttribute("disabled");
			document.getElementById("close-copy-modal").removeAttribute("disabled");
			document.getElementById("copy-spinner").classList.add("d-none");
		});
});
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
        if (!tab) {
            showMessage('No active tab found');
            return;
        }

        const appId = extractAppId(tab.url);

        if (!appId) {
            handleNonGamePage(tab.url);
            return;
        }

        showAppId(appId);
        showStatusContainers();
        await fetchGameData(appId);
    } catch (error) {
        console.error('Popup error:', error);
        showMessage(`Error: ${error.message}`);
    }
});

function extractAppId(url) {
    const match = url.match(/store\.steampowered\.com\/app\/(\d+)/);
    return match ? match[1] : null;
}

function handleNonGamePage(url) {
    if (url.includes('store.steampowered.com')) {
        showMessage(url.endsWith('store.steampowered.com/') ?
            'Please open a game page' :
            'This Steam page is not a game page');
    } else {
        showMessage('Not a Steam game page');
    }
}

function showAppId(appId) {
    document.getElementById('appId').textContent = `App ID: ${appId}`;
}

function showMessage(message) {
    document.getElementById('message').textContent = message;
}

function showStatusContainers() {
    document.getElementById('localServerStatus').style.display = 'block';
    document.getElementById('remoteServerStatus').style.display = 'block';
}

function updateLocalStatus(status, color) {
    const statusElement = document.getElementById('localStatus');
    const statusText = document.getElementById('localStatusText');

    statusElement.style.backgroundColor = color;
    statusText.textContent = `Local: ${status}`;
}

function updateRemoteStatus(status, color) {
    const statusElement = document.getElementById('remoteStatus');
    const statusText = document.getElementById('remoteStatusText');

    statusElement.style.backgroundColor = color;
    statusText.textContent = `Remote: ${status}`;
}

async function fetchGameData(appId) {
    updateLocalStatus('Sending request...', 'orange');
    updateRemoteStatus('Waiting local data', 'gray');

    try {
        // Запрос к локальному серверу
        const localResponse = await fetch(`http://localhost:7123/parse/${appId}`);

        if (!localResponse.ok) {
            throw new Error(`Local server error! status: ${localResponse.status}`);
        }

        const localData = await localResponse.json();
        console.log('Response from local server:', localData);
        updateLocalStatus('Response received', 'green');

        // Извлекаем только price_history из ответа локального сервера
        const priceHistory = localData.price_history;

        if (!priceHistory) {
            throw new Error('No price_history in local server response');
        }

        // Запрос к удаленному серверу с ТОЛЬКО price_history
        await sendToRemoteAPI(priceHistory);
    } catch (error) {
        console.error('Fetch error:', error);
        updateLocalStatus('Request failed', 'red');
        updateRemoteStatus('Failed', 'red');
        showMessage(`Error: ${error.message}`);
    }
}

async function sendToRemoteAPI(priceHistory) {
    updateRemoteStatus('Sending request...', 'orange');
    hideApiResults();  // Скрываем предыдущие результаты

    try {
        const response = await fetch('http://krotoviv.pythonanywhere.com/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ price_history: priceHistory }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Response from remote server:', data);
        updateRemoteStatus('Response received', 'green');

        // Отображаем полученные данные
        displayApiResults(data);
    } catch (error) {
        console.error('Remote API error:', error);
        updateRemoteStatus('Request failed', 'red');
        showMessage(`Remote error: ${error.message}`);
    }
}

function displayApiResults(data) {
    const resultsContainer = document.getElementById('apiResults');
    const predictionElement = document.getElementById('predictionResult');
    const probabilityElement = document.getElementById('probabilityResult');

    // Просто выводим как есть, если сервер уже форматирует
    predictionElement.textContent = data.prediction;
    probabilityElement.textContent = data.probability;

    resultsContainer.style.display = 'block';
}

function hideApiResults() {
    document.getElementById('apiResults').style.display = 'none';
}
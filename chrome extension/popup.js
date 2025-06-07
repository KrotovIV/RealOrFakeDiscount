// Состояние настроек
let settings = {
    highConfidenceOnly: false
};

document.addEventListener('DOMContentLoaded', async () => {
    // Загружаем настройки из хранилища
    await loadSettings();

    // Настройка обработчиков кнопок
    document.getElementById('settings-btn').addEventListener('click', showSettings);
    document.getElementById('back-btn').addEventListener('click', showMainView);

    // Основная логика
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

// Функции для работы с настройками
async function loadSettings() {
    const storedSettings = await chrome.storage.sync.get('settings');
    if (storedSettings.settings) {
        settings = storedSettings.settings;
        document.getElementById('highConfidenceToggle').checked = settings.highConfidenceOnly;
    }
}

async function saveSettings() {
    await chrome.storage.sync.set({ settings });
}

function showSettings() {
    document.getElementById('main-view').style.display = 'none';
    document.getElementById('settings-view').style.display = 'block';
}

function showMainView() {
    document.getElementById('settings-view').style.display = 'none';
    document.getElementById('main-view').style.display = 'block';
}

// Обработчик изменения тумблера
document.getElementById('highConfidenceToggle').addEventListener('change', async function() {
    settings.highConfidenceOnly = this.checked;
    await saveSettings();
});

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

// Обновленная функция displayApiResults
function displayApiResults(data) {
    const resultsContainer = document.getElementById('apiResults');
    const predictionElement = document.getElementById('predictionResult');
    const probabilityElement = document.getElementById('probabilityResult');
    const probabilityContainer = document.getElementById('probabilityContainer');

    // Извлекаем числовое значение вероятности (удаляем % и преобразуем в число)
    const probabilityValue = parseFloat(data.probability.toString().replace('%', ''));

    // Всегда показываем контейнер результатов
    resultsContainer.style.display = 'block';
    console.log('до блока')
    if (settings.highConfidenceOnly) {
        console.log(probabilityValue)
        if (!isNaN(probabilityValue) && probabilityValue >= 90) {
            // Режим "90+%" И вероятность ≥90% - показываем оба значения
            predictionElement.textContent = data.prediction;
            probabilityElement.textContent = data.probability;
            probabilityContainer.style.display = 'block';
        } else {
            // Режим "90+%" И вероятность <90% - показываем "Настоящая" и скрываем вероятность
            predictionElement.textContent = "Настоящая";
            probabilityContainer.style.display = 'none';
        }
    } else {
        // Обычный режим - показываем все данные
        predictionElement.textContent = data.prediction;
        probabilityElement.textContent = data.probability;
        probabilityContainer.style.display = 'block';
    }
}

function hideApiResults() {
    document.getElementById('apiResults').style.display = 'none';
}
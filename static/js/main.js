/**
 * Main JavaScript for face access web UI.
 */

const API_BASE = "/api";
const RECOGNITION_MODE_RADIO = document.querySelectorAll('input[name="mode"]');

let selectedImageBase64 = null;
let selectedVideoBase64 = null;
let enrollImageBase64List = [];
let enrollVideoBase64 = null;

function showLoading(show = true) {
    const loading = document.getElementById("loading");
    loading.style.display = show ? "flex" : "none";
}

function showNotification(message, type = "info", duration = 3000) {
    const notification = document.getElementById("notification");
    notification.textContent = message;
    notification.className = `notification show ${type}`;
    setTimeout(() => notification.classList.remove("show"), duration);
}

function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

function getDecisionLabel(decision) {
    const labels = {
        allow: "РАЗРЕШИТЬ",
        deny: "ОТКАЗ",
        retry: "ПОВТОРИТЬ",
        manual_check: "РУЧНАЯ ПРОВЕРКА",
    };
    return labels[decision] || String(decision || "").toUpperCase();
}

function getDecisionReason(reason) {
    const translated = {
        user_matched_and_access_allowed: "Пользователь найден, доступ разрешен",
        user_not_found: "Пользователь не найден",
        user_not_allowed: "Пользователь не имеет доступа",
        face_not_detected: "Лицо не обнаружено",
        multiple_faces_detected: "Обнаружено несколько лиц",
        ambiguous_match: "Неоднозначное совпадение",
        similarity_not_available: "Похожесть недоступна",
    };
    if (translated[reason]) {
        return translated[reason];
    }
    if ((reason || "").startsWith("quality_not_acceptable:")) {
        return `Недостаточное качество: ${reason.split(": ", 2)[1] || reason}`;
    }
    if ((reason || "").startsWith("liveness_failed:")) {
        return `Проверка живости не пройдена: ${reason.split(": ", 2)[1] || reason}`;
    }
    if ((reason || "").startsWith("similarity_below_threshold:")) {
        return `Похожесть ниже порога: ${reason.split(": ", 2)[1] || reason}`;
    }
    if ((reason || "").startsWith("similarity_review_zone:")) {
        return `Зона проверки: ${reason.split(": ", 2)[1] || reason}`;
    }
    if ((reason || "").startsWith("similarity_below_review_threshold:")) {
        return `Похожесть ниже зоны проверки: ${reason.split(": ", 2)[1] || reason}`;
    }
    return reason || "Неизвестно";
}

function getMatchStatusLabel(status) {
    const labels = {
        matched: "Совпало",
        not_found: "Не найдено",
        low_similarity: "Низкая похожесть",
        ambiguous: "Неоднозначно",
        skipped_due_to_quality: "Пропущено из-за качества",
    };
    return labels[status] || status;
}

function getEventDecisionLabel(decision) {
    const labels = {
        allow: "РАЗРЕШЕНО",
        deny: "ОТКАЗАНО",
        retry: "ПОВТОРИТЬ",
        manual_check: "РУЧНАЯ ПРОВЕРКА",
    };
    return labels[decision] || String(decision || "").toUpperCase();
}

function getDecisionColor(decision) {
    const colors = {
        allow: "#27ae60",
        deny: "#e74c3c",
        retry: "#f39c12",
        manual_check: "#16a085",
    };
    return colors[String(decision || "").toLowerCase()] || "#95a5a6";
}

function setupTabs() {
    document.querySelectorAll(".tab-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const tabName = btn.getAttribute("data-tab");
            document.querySelectorAll(".tab-content").forEach(tab => tab.classList.remove("active"));
            document.querySelectorAll(".tab-btn").forEach(item => item.classList.remove("active"));
            document.getElementById(tabName).classList.add("active");
            btn.classList.add("active");
            if (tabName === "users") loadUsers();
            if (tabName === "events") loadEvents();
        });
    });
}

async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        const statusEl = document.getElementById("health-status");
        const infoEl = document.getElementById("provider-info");
        statusEl.style.color = data.status === "ok" ? "#27ae60" : "#e74c3c";
        infoEl.textContent = `${data.provider} | ${data.users_enrolled} пользователей зарегистрировано`;
    } catch (error) {
        console.error("Проверка состояния не удалась:", error);
    }
}

function setupRecognitionMode() {
    RECOGNITION_MODE_RADIO.forEach(radio => {
        radio.addEventListener("change", () => {
            const mode = document.querySelector('input[name="mode"]:checked').value;
            const input = document.getElementById("claimed-user-id");
            input.style.display = mode === "1to1" ? "block" : "none";
        });
    });
}

function setupDropArea(areaId, inputId, onFiles) {
    const area = document.getElementById(areaId);
    const input = document.getElementById(inputId);

    area.addEventListener("click", () => input.click());
    input.addEventListener("change", async event => {
        const files = Array.from(event.target.files || []);
        if (files.length > 0) {
            await onFiles(files);
        }
    });

    area.addEventListener("dragover", event => {
        event.preventDefault();
        event.currentTarget.classList.add("dragover");
    });
    area.addEventListener("dragleave", event => {
        event.currentTarget.classList.remove("dragover");
    });
    area.addEventListener("drop", async event => {
        event.preventDefault();
        event.currentTarget.classList.remove("dragover");
        const files = Array.from(event.dataTransfer.files || []);
        if (files.length > 0) {
            await onFiles(files);
        }
    });
}

async function processImage() {
    if (!selectedImageBase64) return;
    showLoading(true);
    try {
        const mode = document.querySelector('input[name="mode"]:checked').value;
        const claimedUserId = document.getElementById("claimed-user-id").value || null;
        const response = await fetch(`${API_BASE}/recognize`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                image: selectedImageBase64,
                mode,
                claimed_user_id: claimedUserId,
            }),
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        displayRecognitionResult(data);
        showNotification("Фото обработано успешно", "success");
    } catch (error) {
        showNotification(`Ошибка: ${error.message}`, "error");
    } finally {
        showLoading(false);
    }
}

function displayRecognitionResult(data) {
    const container = document.getElementById("recognition-container");
    const resultsDiv = document.getElementById("recognition-results");
    const imageEl = document.getElementById("recognition-image");
    const qualityDetailsDiv = document.getElementById("quality-details");
    const decisionBoxDiv = document.getElementById("decision-box");

    container.style.display = "block";
    imageEl.src = data.image_display;

    const result = data.recognition_result;
    resultsDiv.innerHTML = `
        <div class="result-item"><span class="result-label">Лицо найдено:</span><span class="result-value">${result.face_detected ? "Да" : "Нет"}</span></div>
        <div class="result-item"><span class="result-label">Количество лиц:</span><span class="result-value">${result.faces_count}</span></div>
        <div class="result-item"><span class="result-label">Проверка живости:</span><span class="result-value">${result.liveness_is_live ? "Прошло" : "Провалено"}</span></div>
        <div class="result-item"><span class="result-label">Статус совпадения:</span><span class="result-value">${getMatchStatusLabel(result.match_status)}</span></div>
        <div class="result-item"><span class="result-label">ID пользователя:</span><span class="result-value">${result.match_user_id || "N/A"}</span></div>
        <div class="result-item"><span class="result-label">Похожесть:</span><span class="result-value">${result.similarity ? result.similarity.toFixed(2) : "N/A"}</span></div>
    `;

    qualityDetailsDiv.innerHTML = `
        <div class="quality-item"><div class="quality-item-label">Оценка качества</div><div class="progress-bar"><div class="progress-fill" style="width: ${result.quality_score * 100}%"></div></div><div class="quality-value">${result.quality_score.toFixed(2)}</div></div>
        <div class="quality-item"><div class="quality-item-label">Размытие</div><div class="progress-bar"><div class="progress-fill" style="width: ${result.blur_score * 100}%"></div></div><div class="quality-value">${result.blur_score.toFixed(2)}</div></div>
        <div class="quality-item"><div class="quality-item-label">Яркость</div><div class="progress-bar"><div class="progress-fill" style="width: ${result.brightness_score * 100}%"></div></div><div class="quality-value">${result.brightness_score.toFixed(2)}</div></div>
        <div class="quality-item"><div class="quality-item-label">Угол лица</div><div class="quality-value">Y: ${result.yaw_angle}° P: ${result.pitch_angle}° R: ${result.roll_angle}°</div></div>
    `;

    const decision = data.decision;
    decisionBoxDiv.className = `decision-box ${decision.decision}`;
    decisionBoxDiv.innerHTML = `
        <div>${getDecisionLabel(decision.decision)}</div>
        <div class="decision-reason">${getDecisionReason(decision.reason)}</div>
        ${decision.user_id ? `<div style="margin-top: 8px; font-size: 14px;">Пользователь: ${decision.user_id}</div>` : ""}
    `;
}

async function processVideo() {
    if (!selectedVideoBase64) return;
    showLoading(true);
    try {
        const response = await fetch(`${API_BASE}/recognize-video`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ video: selectedVideoBase64, max_frames: 30 }),
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        displayVideoResult(data);
        showNotification("Видео обработано успешно", "success");
    } catch (error) {
        showNotification(`Ошибка: ${error.message}`, "error");
    } finally {
        showLoading(false);
    }
}

function displayVideoResult(data) {
    const container = document.getElementById("video-container");
    const timelineEl = document.getElementById("timeline-image");
    const frameTableBody = document.getElementById("frame-table-body");
    const resultsDiv = document.getElementById("video-results");
    const decisionBoxDiv = document.getElementById("video-decision-box");
    container.style.display = "block";
    timelineEl.src =
        'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="800" height="100"><rect width="800" height="100" fill="%23f0f0f0"/><text x="400" y="50" text-anchor="middle" font-family="Arial" font-size="14" fill="%23666">Визуализация кадров</text></svg>';

    frameTableBody.innerHTML = "";
    data.results.forEach(frame => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>#${frame.frame_index}</td>
            <td>${frame.quality_score.toFixed(2)}</td>
            <td>${frame.face_detected ? "Да" : "Нет"}</td>
            <td>${frame.selected ? "Выбран" : frame.face_detected ? "Годный" : "Нет лица"}</td>
        `;
        if (frame.selected) row.style.background = "#d4edda";
        frameTableBody.appendChild(row);
    });

    if (data.final_result) {
        const result = data.final_result;
        resultsDiv.innerHTML = `
            <div class="result-item"><span class="result-label">Лучший кадр:</span><span class="result-value">#${data.best_frame_index || "N/A"}</span></div>
            <div class="result-item"><span class="result-label">Качество:</span><span class="result-value">${result.quality_score.toFixed(2)}</span></div>
            <div class="result-item"><span class="result-label">Совпадение:</span><span class="result-value">${getMatchStatusLabel(result.match_status)}</span></div>
            <div class="result-item"><span class="result-label">Похожесть:</span><span class="result-value">${result.similarity ? result.similarity.toFixed(2) : "N/A"}</span></div>
        `;
    }

    if (data.final_decision) {
        const decision = data.final_decision;
        decisionBoxDiv.className = `decision-box ${decision.decision}`;
        decisionBoxDiv.innerHTML = `
            <div>${getDecisionLabel(decision.decision)}</div>
            <div class="decision-reason">${getDecisionReason(decision.reason)}</div>
        `;
    }
}

function renderEnrollPreviews() {
    const list = document.getElementById("enroll-preview-list");
    list.innerHTML = "";
    if (enrollImageBase64List.length === 0) {
        list.style.display = "none";
        return;
    }
    enrollImageBase64List.forEach((image, idx) => {
        const item = document.createElement("div");
        item.className = "enroll-preview-item";
        item.innerHTML = `
            <img src="${image}" alt="Фото ${idx + 1}" class="enroll-preview-image">
            <div class="enroll-preview-index">#${idx + 1}</div>
        `;
        list.appendChild(item);
    });
    list.style.display = "grid";
}

function appendUniqueEnrollImages(base64Images) {
    for (const image of base64Images) {
        if (!enrollImageBase64List.includes(image)) {
            enrollImageBase64List.push(image);
        }
    }
}

async function enrollFromPhotos() {
    const fullName = document.getElementById("enroll-full-name").value.trim();
    if (!fullName) {
        showNotification("Введите ФИО пользователя", "warning");
        return;
    }
    if (enrollImageBase64List.length === 0) {
        showNotification("Выберите хотя бы одно фото", "warning");
        return;
    }

    showLoading(true);
    try {
        const response = await fetch(`${API_BASE}/enroll`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                full_name: fullName,
                images: enrollImageBase64List,
            }),
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();

        const resultDiv = document.getElementById("enroll-result");
        const statusDiv = document.getElementById("enroll-status");
        if (data.success) {
            statusDiv.className = "alert success";
            statusDiv.textContent = `Регистрация завершена. ФИО: ${data.full_name || fullName}. Внутренний ID: ${data.user_id}. Загружено фото: ${data.enrolled_images}.`;
            showNotification("Пользователь зарегистрирован", "success");
            document.getElementById("enroll-image-input").value = "";
            enrollImageBase64List = [];
            renderEnrollPreviews();
            document.getElementById("enroll-btn").disabled = true;
        } else {
            statusDiv.className = "alert error";
            statusDiv.textContent = `Ошибка регистрации: ${data.message}`;
            showNotification(data.message, "error");
        }
        resultDiv.style.display = "block";
        await loadUsers();
    } catch (error) {
        showNotification(`Ошибка: ${error.message}`, "error");
    } finally {
        showLoading(false);
    }
}

async function enrollFromVideo() {
    const fullName = document.getElementById("enroll-full-name").value.trim();
    if (!fullName) {
        showNotification("Введите ФИО пользователя", "warning");
        return;
    }
    if (!enrollVideoBase64) {
        showNotification("Выберите видео", "warning");
        return;
    }

    showLoading(true);
    try {
        const response = await fetch(`${API_BASE}/enroll-video`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                full_name: fullName,
                video: enrollVideoBase64,
                max_frames: 30,
                max_templates: 5,
            }),
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();

        const resultDiv = document.getElementById("enroll-result");
        const statusDiv = document.getElementById("enroll-status");
        if (data.success) {
            statusDiv.className = "alert success";
            statusDiv.textContent = `Видео-регистрация завершена. ФИО: ${data.full_name || fullName}. Внутренний ID: ${data.user_id}. Шаблонов создано: ${data.templates_created}.`;
            showNotification("Видео-регистрация выполнена успешно", "success");
            document.getElementById("enroll-video-input").value = "";
            enrollVideoBase64 = null;
            document.getElementById("enroll-video-btn").disabled = true;
        } else {
            statusDiv.className = "alert error";
            statusDiv.textContent = `Ошибка видео-регистрации: ${data.message}`;
            showNotification(data.message, "error");
        }
        resultDiv.style.display = "block";
        await loadUsers();
    } catch (error) {
        showNotification(`Ошибка: ${error.message}`, "error");
    } finally {
        showLoading(false);
    }
}

async function loadUsers() {
    try {
        const response = await fetch(`${API_BASE}/users`);
        const data = await response.json();
        const usersList = document.getElementById("users-list");
        usersList.innerHTML = "";
        if (data.users.length === 0) {
            usersList.innerHTML = '<p style="text-align: center; color: #999;">Пользователи пока не зарегистрированы</p>';
            return;
        }
        data.users.forEach(user => {
            const item = document.createElement("div");
            item.className = "user-item";
            item.innerHTML = `
                <div class="item-title">${user.full_name || "Без ФИО"}</div>
                <div class="item-detail">Внутренний ID: ${user.user_id}</div>
                <div class="item-detail">Шаблонов: ${user.templates_count}</div>
                <div class="item-detail">Доступ: ${user.access_allowed ? "Разрешен" : "Запрещен"}</div>
            `;
            usersList.appendChild(item);
        });
    } catch (error) {
        console.error("Ошибка загрузки пользователей:", error);
        showNotification("Не удалось загрузить пользователей", "error");
    }
}

async function loadEvents() {
    try {
        const response = await fetch(`${API_BASE}/events?limit=50`);
        const data = await response.json();
        const eventsList = document.getElementById("events-list");
        eventsList.innerHTML = "";
        if (data.events.length === 0) {
            eventsList.innerHTML = '<p style="text-align: center; color: #999;">Событий пока нет</p>';
            return;
        }
        data.events.forEach(event => {
            const item = document.createElement("div");
            item.className = "event-item";
            item.innerHTML = `
                <div class="item-title">
                    <span style="display: inline-block; padding: 4px 8px; border-radius: 4px; background: ${getDecisionColor(event.decision)}; color: white; font-size: 12px; margin-right: 10px;">
                        ${getEventDecisionLabel(event.decision)}
                    </span>
                    ${event.timestamp}
                </div>
                <div class="item-detail">Пользователь: ${event.user_id || "Неизвестно"}</div>
                <div class="item-detail">Причина: ${getDecisionReason(event.reason)}</div>
                ${event.similarity !== null ? `<div class="item-detail">Похожесть: ${event.similarity.toFixed(2)}</div>` : ""}
                ${event.quality_score !== null ? `<div class="item-detail">Качество: ${event.quality_score.toFixed(2)}</div>` : ""}
            `;
            eventsList.appendChild(item);
        });
    } catch (error) {
        console.error("Ошибка загрузки событий:", error);
        showNotification("Не удалось загрузить события", "error");
    }
}

function setupEventActions() {
    document.getElementById("refresh-events").addEventListener("click", loadEvents);
    document.getElementById("export-events").addEventListener("click", async () => {
        try {
            const response = await fetch(`${API_BASE}/events?limit=1000`);
            const data = await response.json();
            const headers = ["ID события", "Время", "ID пользователя", "Решение", "Причина", "Похожесть", "Качество"];
            const rows = data.events.map(event => [
                event.event_id,
                event.timestamp,
                event.user_id || "",
                getEventDecisionLabel(event.decision),
                getDecisionReason(event.reason),
                event.similarity || "",
                event.quality_score || "",
            ]);
            const csv = [headers, ...rows].map(row => row.map(cell => `"${cell}"`).join(",")).join("\n");
            const blob = new Blob([csv], { type: "text/csv" });
            const url = window.URL.createObjectURL(blob);
            const anchor = document.createElement("a");
            anchor.href = url;
            anchor.download = `events_${new Date().toISOString().split("T")[0]}.csv`;
            anchor.click();
            showNotification("События экспортированы", "success");
        } catch (error) {
            showNotification("Не удалось экспортировать события", "error");
        }
    });
}

function setupHandlers() {
    setupDropArea("recognition-upload", "image-input", async files => {
        selectedImageBase64 = await fileToBase64(files[0]);
        await processImage();
    });

    setupDropArea("video-upload", "video-input", async files => {
        selectedVideoBase64 = await fileToBase64(files[0]);
        await processVideo();
    });

    setupDropArea("enroll-upload", "enroll-image-input", async files => {
        const imageFiles = files.filter(file => file.type.startsWith("image/"));
        const newImages = [];
        for (const file of imageFiles) {
            newImages.push(await fileToBase64(file));
        }
        appendUniqueEnrollImages(newImages);
        renderEnrollPreviews();
        document.getElementById("enroll-btn").disabled = enrollImageBase64List.length === 0;
    });

    setupDropArea("enroll-video-upload", "enroll-video-input", async files => {
        enrollVideoBase64 = await fileToBase64(files[0]);
        document.getElementById("enroll-video-btn").disabled = false;
    });

    document.getElementById("enroll-btn").addEventListener("click", enrollFromPhotos);
    document.getElementById("enroll-video-btn").addEventListener("click", enrollFromVideo);
}

document.addEventListener("DOMContentLoaded", () => {
    setupTabs();
    setupRecognitionMode();
    setupHandlers();
    setupEventActions();
    checkHealth();
    setInterval(checkHealth, 30000);
});

const SETTINGS_KEYS = {
    reducedMotion: "schologyReducedMotion",
    showAssignments: "schologyShowAssignments",
    viewMode: "courseMaterialsViewMode",
    sortMode: "courseMaterialsSortMode"
}

const RETRY_DELAY_MS = 1000
const MAX_RETRY_DELAY_MS = 10000

function shouldRetryResponse(response) {
    return response.status === 408 || response.status === 429 || response.status >= 500
}

function wait(milliseconds) {
    return new Promise((resolve) => setTimeout(resolve, milliseconds))
}

async function fetchWithRetry(...argumentsList) {
    let delay = RETRY_DELAY_MS

    while (true) {
        try {
            const response = await fetch(...argumentsList)
            if (!shouldRetryResponse(response)) {
                return response
            }

            throw new Error(`Server returned ${response.status}`)
        }
        catch (error) {
            console.error("Request failed; retrying:", error)
            await wait(delay)
            delay = Math.min(delay * 2, MAX_RETRY_DELAY_MS)
        }
    }
}

window.fetchWithRetry = fetchWithRetry

function getStoredSetting(key, fallback) {
    try {
        const value = localStorage.getItem(key)
        return value === null ? fallback : value
    }
    catch (error) {
        console.error("Unable to read setting:", error)
        return fallback
    }
}

function applyStoredSettings() {
    const root = document.documentElement
    const body = document.body

    root.dataset.reducedMotion = getStoredSetting(SETTINGS_KEYS.reducedMotion, "false")
    body.dataset.showAssignments = getStoredSetting(SETTINGS_KEYS.showAssignments, "true")
}

function updateSettingsLinks() {
    document.querySelectorAll(".settings-link").forEach((link) => {
        if (link.id === "return-link") {
            return
        }

        const returnPath = `${window.location.pathname}${window.location.search}`
        link.href = `/settings?return=${encodeURIComponent(returnPath)}`
    })
}

document.addEventListener("DOMContentLoaded", () => {
    applyStoredSettings()
    updateSettingsLinks()
})

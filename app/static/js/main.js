document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initFlashMessages();
    initPayloadButtons();
    initUploadZone();
});

/** Theme Switcher (Dark/Light Mode) */
function initTheme() {
    const themeBtn = document.getElementById('theme-toggle');
    if (!themeBtn) return;

    const currentTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', currentTheme);
    updateThemeIcon(currentTheme);

    themeBtn.addEventListener('click', () => {
        let theme = document.documentElement.getAttribute('data-theme');
        let newTheme = theme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);
    });
}

function updateThemeIcon(theme) {
    const icon = document.querySelector('#theme-toggle img');
    if (icon) {
        icon.src = `/static/icons/${theme === 'dark' ? 'sun' : 'moon'}.svg`;
    }
}

/** Auto-dismiss flash messages after 5 seconds */
function initFlashMessages() {
    const flashes = document.querySelectorAll('.flash-message');
    flashes.forEach((flash) => {
        setTimeout(() => {
            flash.style.animation = 'slideIn 0.3s ease reverse';
            setTimeout(() => flash.remove(), 300);
        }, 5000);

        flash.addEventListener('click', () => {
            flash.style.animation = 'slideIn 0.3s ease reverse';
            setTimeout(() => flash.remove(), 300);
        });
    });
}

/** Payload items auto-fill the search/input field */
function initPayloadButtons() {
    document.querySelectorAll('.payload-item').forEach((item) => {
        item.addEventListener('click', () => {
            const value = item.dataset.payload;
            if (!value) return;

            const targetId = item.dataset.target || 'search-input';
            const input = document.getElementById(targetId);
            if (input) {
                input.value = value;
                input.focus();
                input.dispatchEvent(new Event('input'));

                // Visual feedback
                item.style.borderColor = 'var(--accent-green)';
                setTimeout(() => {
                    item.style.borderColor = '';
                }, 600);
            }
        });
    });
}

/** Drag-and-drop upload zone */
function initUploadZone() {
    const zone = document.querySelector('.upload-zone');
    if (!zone) return;

    zone.addEventListener('dragover', (e) => {
        e.preventDefault();
        zone.classList.add('dragover');
    });

    zone.addEventListener('dragleave', () => {
        zone.classList.remove('dragover');
    });

    zone.addEventListener('drop', (e) => {
        zone.classList.remove('dragover');
    });
}

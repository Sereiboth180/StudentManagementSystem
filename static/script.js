document.addEventListener('DOMContentLoaded', () => {
    // 1. Theme Switcher Logic
    const themeBtns = document.querySelectorAll('.theme-btn');
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    // Apply saved theme or system setting on startup
    if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
        document.documentElement.setAttribute('data-theme', 'dark');
        updateAllThemeButtons(true);
    } else {
        document.documentElement.setAttribute('data-theme', 'light');
        updateAllThemeButtons(false);
    }

    // Attach click events to all theme buttons
    themeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const isDark = currentTheme === 'dark';
            const nextTheme = isDark ? 'light' : 'dark';

            document.documentElement.setAttribute('data-theme', nextTheme);
            localStorage.setItem('theme', nextTheme);
            updateAllThemeButtons(!isDark);
        });
    });

    function updateAllThemeButtons(isDark) {
        document.querySelectorAll('.theme-icon').forEach(icon => {
            icon.textContent = isDark ? '☀️' : '🌙';
        });
        document.querySelectorAll('.theme-text').forEach(text => {
            text.textContent = isDark ? 'Light' : 'Dark';
        });
    }

    // 2. Drag & Drop Visual Indication for File Upload
    const dropZone = document.querySelector('.drop-zone');
    const fileInput = document.getElementById('csv-file-input');

    if (dropZone && fileInput) {
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropZone.style.borderColor = 'var(--primary-color)';
                dropZone.style.backgroundColor = 'var(--secondary-hover)';
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropZone.style.borderColor = 'var(--border-color)';
                dropZone.style.backgroundColor = 'var(--secondary-bg)';
            }, false);
        });

        dropZone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;

            if (files.length > 0) {
                fileInput.files = files;
                fileInput.form.submit();
            }
        });
    }
});

import React from 'react';

function ThemeSwitcher() {
    const toggleTheme = () => {
        document.body.classList.toggle('dark-theme');
    };

    return (
        <button className="theme-switcher" onClick={toggleTheme}>Switch Theme</button>
    );
}

export default ThemeSwitcher;

odoo.define('ez_font.inject_css', function (require) {
    'use strict';
    
    const rpc = require('web.rpc');
    
    /**
     * Inject Ez Font CSS dynamically
     */
    function injectEzFontCSS() {
        // Check if CSS link already exists
        if (document.getElementById('ez-font-dynamic-link')) {
            return;
        }
        
        // Create and inject the link tag
        const link = document.createElement('link');
        link.id = 'ez-font-dynamic-link';
        link.rel = 'stylesheet';
        link.type = 'text/css';
        link.href = '/ez_font/get_css?t=' + Date.now(); // Add timestamp for cache busting
        
        document.head.appendChild(link);
    }
    
    // Inject CSS when page loads
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', injectEzFontCSS);
    } else {
        injectEzFontCSS();
    }
    
    // Also watch for DOM changes to re-inject if needed
    const observer = new MutationObserver(function(mutations) {
        if (!document.getElementById('ez-font-dynamic-link')) {
            injectEzFontCSS();
        }
    });
    
    observer.observe(document.head, {
        childList: true,
        subtree: true
    });
});

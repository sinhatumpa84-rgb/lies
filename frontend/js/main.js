/* ===================================
   TRUTHLENS AI - Main JavaScript
   ==================================== */

document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
    initializeAnimations();
});

// Navigation toggle
function initializeNavigation() {
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');

    if (hamburger) {
        hamburger.addEventListener('click', () => {
            navLinks.style.display = navLinks.style.display === 'flex' ? 'none' : 'flex';
            navLinks.style.position = 'absolute';
            navLinks.style.top = '60px';
            navLinks.style.left = '0';
            navLinks.style.right = '0';
            navLinks.style.flexDirection = 'column';
            navLinks.style.background = 'rgba(10, 14, 39, 0.95)';
            navLinks.style.backdropFilter = 'blur(10px)';
            navLinks.style.borderBottom = '1px solid rgba(0, 212, 255, 0.1)';
        });

        // Close menu on link click
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                if (navLinks.style.display === 'flex') {
                    navLinks.style.display = 'none';
                }
            });
        });
    }
}

// Initialize animations on scroll
function initializeAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    document.querySelectorAll('.feature-card, .process-step, .trust-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'all 0.6s ease-out';
        observer.observe(el);
    });
}

// Smooth scroll behavior
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});

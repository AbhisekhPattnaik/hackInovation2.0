// ── Slow the background video to 40% normal speed ──
const bgVideo = document.querySelector('.video-bg video');
bgVideo.playbackRate = 0.4;
bgVideo.addEventListener('loadedmetadata', () => {
    bgVideo.playbackRate = 0.4;
});

// ── Ripple effect on Explore button click ──
const btn = document.getElementById('exploreBtn');
btn.addEventListener('click', function (e) {
    const rect = btn.getBoundingClientRect();
    const ripple = document.createElement('span');
    const size = Math.max(rect.width, rect.height);
    ripple.className = 'ripple';
    ripple.style.cssText = `
        width:  ${size}px;
        height: ${size}px;
        left:   ${e.clientX - rect.left - size / 2}px;
        top:    ${e.clientY - rect.top  - size / 2}px;
    `;
    btn.appendChild(ripple);
    ripple.addEventListener('animationend', () => ripple.remove());
});

import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./Explore.css";

export default function Explore() {
  const navigate = useNavigate();

  useEffect(() => {
    // Slow the background video to 40% normal speed
    const bgVideo = document.querySelector(".video-bg video");
    if (bgVideo) {
      bgVideo.playbackRate = 0.4;
      bgVideo.addEventListener("loadedmetadata", () => {
        bgVideo.playbackRate = 0.4;
      });
    }

    // Ripple effect on Explore button click
    const btn = document.getElementById("exploreBtn");
    if (btn) {
      btn.addEventListener("click", function (e) {
        const rect = btn.getBoundingClientRect();
        const ripple = document.createElement("span");
        const size = Math.max(rect.width, rect.height);
        ripple.className = "ripple";
        ripple.style.cssText = `
          width:  ${size}px;
          height: ${size}px;
          left:   ${e.clientX - rect.left - size / 2}px;
          top:    ${e.clientY - rect.top - size / 2}px;
        `;
        btn.appendChild(ripple);
        ripple.addEventListener("animationend", () => ripple.remove());
      });
    }
  }, []);

  const handleExploreClick = () => {
    navigate("/login");
  };

  return (
    <>
      {/* Video Background */}
      <div className="video-bg">
        <video autoPlay muted loop playsInline>
          <source src="/explore-bg.mp4" type="video/mp4" />
        </video>
      </div>

      {/* Centre Stage */}
      <div className="stage">
        {/* Medical cross icon */}
        <div className="med-cross">
          <span></span>
          <span></span>
          <span></span>
          <span></span>
          <span></span>
          <span></span>
          <span></span>
          <span></span>
          <span></span>
        </div>

        <span className="tagline">Advanced Healthcare &nbsp;·&nbsp; AI-Powered Care</span>

        {/* Button with pulse rings */}
        <div className="btn-wrapper">
          <div className="pulse-ring"></div>
          <div className="pulse-ring"></div>
          <div className="pulse-ring"></div>

          <button className="explore-btn" id="exploreBtn" onClick={handleExploreClick}>
            {/* Scanning EKG on hover */}
            <div className="ekg-line">
              <svg viewBox="0 0 200 14" preserveAspectRatio="none">
                <polyline
                  points="
                    0,7 30,7 40,7 45,1 50,13 55,1 60,7
                    80,7 90,7 95,2 100,12 105,2 110,7
                    130,7 140,7 145,2 150,12 155,2 160,7
                    180,7 200,7"
                />
              </svg>
            </div>

            <div className="btn-inner">
              <div className="btn-pulse-dot"></div>
              <span className="btn-text">Login</span>
              <svg
                className="btn-icon"
                viewBox="0 0 24 24"
                fill="none"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <line x1="5" y1="12" x2="19" y2="12" />
                <polyline points="12 5 19 12 12 19" />
              </svg>
            </div>
          </button>
        </div>

        <span className="subtitle">Your health, our priority</span>
      </div>

      {/* ECG bottom bar */}
      <div className="ecg-bar">
        <svg viewBox="0 0 800 48" preserveAspectRatio="none">
          <polyline
            points="
              0,24 60,24 80,24 90,6  100,42 110,6  120,24
              160,24 180,24 190,6  200,42 210,6  220,24
              260,24 280,24 290,6  300,42 310,6  320,24
              360,24 380,24 390,6  400,42 410,6  420,24
              460,24 480,24 490,6  500,42 510,6  520,24
              560,24 580,24 590,6  600,42 610,6  620,24
              660,24 680,24 690,6  700,42 710,6  720,24
              760,24 800,24"
          />
          <polyline
            points="
              800,24 860,24 880,24 890,6  900,42 910,6  920,24
              960,24 980,24 990,6 1000,42 1010,6 1020,24
              1060,24 1080,24 1090,6 1100,42 1110,6 1120,24
              1160,24 1180,24 1190,6 1200,42 1210,6 1220,24
              1260,24 1280,24 1290,6 1300,42 1310,6 1320,24
              1360,24 1380,24 1390,6 1400,42 1410,6 1420,24
              1460,24 1480,24 1490,6 1500,42 1510,6 1520,24
              1560,24 1600,24"
          />
        </svg>
      </div>
    </>
  );
}

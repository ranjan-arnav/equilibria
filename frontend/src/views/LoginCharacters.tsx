import { useEffect, useRef } from 'react';
import './LoginCharacters.css';

interface LoginCharactersProps {
    lookAway: boolean;
}

export const LoginCharacters = ({ lookAway }: LoginCharactersProps) => {
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            if (lookAway) return;

            const pupils = document.querySelectorAll('.pupil');
            const seesawPupils = document.querySelectorAll('.seesaw-pupil');

            const movePupils = (elements: NodeListOf<Element>, limit: number, scale: number) => {
                elements.forEach((el) => {
                    const pupil = el as HTMLElement;
                    const socket = pupil.parentElement;
                    if (!socket) return;

                    const rect = socket.getBoundingClientRect();
                    const centerX = rect.left + rect.width / 2;
                    const centerY = rect.top + rect.height / 2;

                    const angle = Math.atan2(e.clientY - centerY, e.clientX - centerX);
                    const dist = Math.min(limit, Math.hypot(e.clientX - centerX, e.clientY - centerY) / scale);

                    pupil.style.transform = `translate(calc(-50% + ${Math.cos(angle) * dist}px), calc(-50% + ${Math.sin(angle) * dist}px))`;
                });
            };

            movePupils(pupils, 7, 25);
            movePupils(seesawPupils, 2, 40);
        };

        window.addEventListener('mousemove', handleMouseMove);
        return () => window.removeEventListener('mousemove', handleMouseMove);
    }, [lookAway]);

    return (
        <div ref={containerRef} className={`shapes-area ${lookAway ? 'look-away' : ''}`}>
            {/* GUARD CHARACTER 1 WITH BARBELL */}
            <div className="shape" data-type="guard1">
                <div className="eyes-row">
                    <div className="eye-socket"><div className="pupil"></div></div>
                    <div className="eye-socket"><div className="pupil"></div></div>
                </div>
                <div className="hand-wrapper">
                    <div className="barbell"></div>
                    <svg className="hand-svg left" viewBox="0 0 60 80">
                        <path d="M30,10 Q35,8 38,12 L40,25 Q40,30 35,32 L32,33 Q30,35 28,33 L15,30 Q12,28 12,25 L10,15 Q8,10 12,8 Q18,6 22,10 L25,15 L28,12 Q30,10 30,10 Z M35,30 Q36,32 34,34 L28,36 L25,34 Q24,32 25,30 Z" />
                    </svg>
                    <svg className="hand-svg right" viewBox="0 0 60 80">
                        <path d="M30,10 Q35,8 38,12 L40,25 Q40,30 35,32 L32,33 Q30,35 28,33 L15,30 Q12,28 12,25 L10,15 Q8,10 12,8 Q18,6 22,10 L25,15 L28,12 Q30,10 30,10 Z M35,30 Q36,32 34,34 L28,36 L25,34 Q24,32 25,30 Z" />
                    </svg>
                </div>
            </div>

            {/* EXERCISER WITH DUMBBELLS */}
            <div className="shape exerciser" data-type="exerciser">
                <div className="eyes-row">
                    <div className="eye-socket"><div className="pupil"></div></div>
                    <div className="eye-socket"><div className="pupil"></div></div>
                </div>
                <div className="hand-wrapper">
                    <svg className="hand-svg left" viewBox="0 0 60 80">
                        <path d="M30,10 Q35,8 38,12 L40,25 Q40,30 35,32 L32,33 Q30,35 28,33 L15,30 Q12,28 12,25 L10,15 Q8,10 12,8 Q18,6 22,10 L25,15 L28,12 Q30,10 30,10 Z M35,30 Q36,32 34,34 L28,36 L25,34 Q24,32 25,30 Z" />
                        <foreignObject x="10" y="5" width="40" height="30">
                            <div className="dumbbell"></div>
                        </foreignObject>
                    </svg>
                    <svg className="hand-svg right" viewBox="0 0 60 80">
                        <path d="M30,10 Q35,8 38,12 L40,25 Q40,30 35,32 L32,33 Q30,35 28,33 L15,30 Q12,28 12,25 L10,15 Q8,10 12,8 Q18,6 22,10 L25,15 L28,12 Q30,10 30,10 Z M35,30 Q36,32 34,34 L28,36 L25,34 Q24,32 25,30 Z" />
                        <foreignObject x="10" y="5" width="40" height="30">
                            <div className="dumbbell"></div>
                        </foreignObject>
                    </svg>
                </div>
            </div>

            {/* SEESAW */}
            <div className="seesaw-section">
                <div className="seesaw-container">
                    <div className="seesaw-base" id="seesawBase">
                        <div className="seesaw-character left">
                            <div className="seesaw-head">
                                <div className="seesaw-eye"><div className="seesaw-pupil"></div></div>
                                <div className="seesaw-eye"><div className="seesaw-pupil"></div></div>
                            </div>
                            <div className="seesaw-body"></div>
                        </div>
                        <div className="seesaw-character right">
                            <div className="seesaw-head">
                                <div className="seesaw-eye"><div className="seesaw-pupil"></div></div>
                                <div className="seesaw-eye"><div className="seesaw-pupil"></div></div>
                            </div>
                            <div className="seesaw-body"></div>
                        </div>
                    </div>
                    <div className="seesaw-pivot"></div>
                </div>
            </div>
        </div>
    );
};

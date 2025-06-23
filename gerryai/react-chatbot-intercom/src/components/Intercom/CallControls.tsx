import React from 'react';

const CallControls: React.FC = () => {
    const handleStartCall = () => {
        // Logic to start a call
    };

    const handleEndCall = () => {
        // Logic to end a call
    };

    return (
        <div className="call-controls">
            <button onClick={handleStartCall}>Start Call</button>
            <button onClick={handleEndCall}>End Call</button>
        </div>
    );
};

export default CallControls;
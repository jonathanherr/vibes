import React from 'react';

const QuickActions: React.FC = () => {
    const handleAction = (action: string) => {
        // Implement action handling logic here
        console.log(`Action triggered: ${action}`);
    };

    return (
        <div className="quick-actions">
            <button onClick={() => handleAction('sendMessage')}>Send Message</button>
            <button onClick={() => handleAction('makeCall')}>Make Call</button>
            <button onClick={() => handleAction('sendImage')}>Send Image</button>
            <button onClick={() => handleAction('sendVideo')}>Send Video</button>
        </div>
    );
};

export default QuickActions;
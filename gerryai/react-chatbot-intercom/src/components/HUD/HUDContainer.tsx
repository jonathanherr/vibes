import React from 'react';
import RecentQueries from './RecentQueries';
import QuickActions from './QuickActions';

const HUDContainer: React.FC = () => {
    // Mock data for recent queries
    const mockQueries = [
        { id: 1, question: "What's the weather like today?", answer: "It's sunny and 72°F outside." },
        { id: 2, question: "Set a timer for 10 minutes", answer: "Timer set for 10 minutes." },
        { id: 3, question: "What time is dinner?", answer: "Dinner is scheduled for 6:30 PM." }
    ];

    return (
        <div className="hud-container">
            <RecentQueries queries={mockQueries} />
            <QuickActions />
        </div>
    );
};

export default HUDContainer;
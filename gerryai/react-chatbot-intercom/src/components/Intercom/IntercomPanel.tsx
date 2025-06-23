import React from 'react';
import useIntercom from '../../hooks/useIntercom';
import TabletList from './TabletList';
import CallControls from './CallControls';

const IntercomPanel: React.FC = () => {
    const { connectedTablets, startCall, endCall } = useIntercom();

    const handleTabletSelect = (tablet: string) => {
        startCall(tablet);
    };

    return (
        <div className="intercom-panel">
            <h2>Intercom System</h2>
            <TabletList tablets={connectedTablets} onSelect={handleTabletSelect} />
            <CallControls />
        </div>
    );
};

export default IntercomPanel;
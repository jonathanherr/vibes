import React from 'react';

const TabletList: React.FC<{ tablets: string[]; onSelect: (tablet: string) => void }> = ({ tablets, onSelect }) => {
    return (
        <div className="tablet-list">
            <h2>Connected Tablets</h2>
            <ul>
                {tablets.map((tablet, index) => (
                    <li key={index} onClick={() => onSelect(tablet)}>
                        {tablet}
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default TabletList;
import React from 'react';
import { Link } from 'react-router-dom';

const Header: React.FC = () => {
    return (
        <header className="header">
            <h1>Chatbot Intercom System</h1>
            <nav>
                <ul style={{ 
                    listStyle: 'none', 
                    display: 'flex', 
                    gap: '20px', 
                    margin: 0, 
                    padding: 0 
                }}>
                    <li>
                        <Link 
                            to="/chat" 
                            style={{ 
                                color: 'white', 
                                textDecoration: 'none',
                                padding: '8px 16px',
                                borderRadius: '4px'
                            }}
                        >
                            Chat
                        </Link>
                    </li>
                    <li>
                        <Link 
                            to="/hud" 
                            style={{ 
                                color: 'white', 
                                textDecoration: 'none',
                                padding: '8px 16px',
                                borderRadius: '4px'
                            }}
                        >
                            HUD
                        </Link>
                    </li>
                    <li>
                        <Link 
                            to="/intercom" 
                            style={{ 
                                color: 'white', 
                                textDecoration: 'none',
                                padding: '8px 16px',
                                borderRadius: '4px'
                            }}
                        >
                            Intercom
                        </Link>
                    </li>
                </ul>
            </nav>
        </header>
    );
};

export default Header;
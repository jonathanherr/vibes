import React, { useState } from 'react';

interface ImageViewerProps {
    src: string;
    alt?: string;
    width?: number;
    height?: number;
    className?: string;
}

const ImageViewer: React.FC<ImageViewerProps> = ({ 
    src, 
    alt, 
    width, 
    height, 
    className = '' 
}) => {
    const [isLoading, setIsLoading] = useState(true);
    const [hasError, setHasError] = useState(false);
    const [showFullsize, setShowFullsize] = useState(false);

    const handleImageLoad = () => {
        setIsLoading(false);
        setHasError(false);
    };

    const handleImageError = () => {
        setIsLoading(false);
        setHasError(true);
    };

    const handleImageClick = () => {
        setShowFullsize(true);
    };

    const handleCloseFullsize = () => {
        setShowFullsize(false);
    };

    if (hasError) {
        return (
            <div className={`image-viewer error ${className}`}>
                <div className="error-message">
                    ❌ Failed to load image
                </div>
            </div>
        );
    }

    return (
        <>
            <div className={`image-viewer ${className}`}>
                {isLoading && (
                    <div className="loading-placeholder" style={{ width, height }}>
                        <div className="loading-spinner">🔄 Loading image...</div>
                    </div>
                )}
                <img 
                    src={src} 
                    alt={alt || 'Generated image'} 
                    style={{ 
                        width, 
                        height,
                        display: isLoading ? 'none' : 'block',
                        cursor: 'pointer',
                        borderRadius: '8px',
                        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
                    }}
                    onLoad={handleImageLoad}
                    onError={handleImageError}
                    onClick={handleImageClick}
                />
            </div>

            {showFullsize && (
                <div 
                    className="fullsize-overlay" 
                    onClick={handleCloseFullsize}
                    style={{
                        position: 'fixed',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        zIndex: 1000,
                        cursor: 'pointer'
                    }}
                >
                    <img 
                        src={src} 
                        alt={alt || 'Generated image'}
                        style={{
                            maxWidth: '90vw',
                            maxHeight: '90vh',
                            objectFit: 'contain'
                        }}
                        onClick={(e) => e.stopPropagation()}
                    />
                    <button 
                        onClick={handleCloseFullsize}
                        style={{
                            position: 'absolute',
                            top: '20px',
                            right: '20px',
                            background: 'white',
                            border: 'none',
                            borderRadius: '50%',
                            width: '40px',
                            height: '40px',
                            fontSize: '20px',
                            cursor: 'pointer'
                        }}
                    >
                        ×
                    </button>
                </div>
            )}
        </>
    );
};

export default ImageViewer;
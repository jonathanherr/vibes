import React from 'react';

interface ImageViewerProps {
    src: string;
    alt?: string;
}

const ImageViewer: React.FC<ImageViewerProps> = ({ src, alt }) => {
    return (
        <div className="image-viewer">
            <img src={src} alt={alt || 'Image'} />
        </div>
    );
};

export default ImageViewer;
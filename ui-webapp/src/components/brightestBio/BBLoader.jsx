
import React from 'react';

const LOADER_SIZES = Object.freeze({
    xs: { width: 16, height: 9 },
    sm: { width: 32, height: 18 },
    md: { width: 64, height: 36 },
    lg: { width: 128, height: 72 },
    xl: { width: 256, height: 144 },
});

export const BBLoader = ({
    size = 'sm',
    duration = 1.5
}) => {
    const { width, height } = LOADER_SIZES[size];
    return (
        <div className="bb-loader">
            <svg width={`${width}px`} height={`${height}px`} viewBox="0 0 120 30" xmlns="http://www.w3.org/2000/svg" role="presentation">
                <circle cx="15" cy="15" r="100" fill="#2E74BA">
                    <animate attributeName="r" from="15" to="15" begin="0s" dur={`${duration}s`} values="10;10;10" calcMode="linear" repeatCount="indefinite"></animate>
                    <animate attributeName="fill-opacity" from="1" to="1" begin="0s" dur={`${duration}s`} values="0;.5;1;1;1;1;1" calcMode="linear" repeatCount="indefinite"></animate>
                </circle>
                <circle cx="60" cy="15" r="9" fillOpacity="0.3" fill="#FAB611">
                    <animate attributeName="r" from="9" to="9" begin="0s" dur={`${duration}s`} values="12;12;12" calcMode="linear" repeatCount="indefinite"></animate>
                    <animate attributeName="fill-opacity" from="0.5" to="0.5" begin="0s" dur={`${duration}s`} values="0;0;.5;1;1;1;1" calcMode="linear" repeatCount="indefinite"></animate>
                </circle>
                <circle cx="105" cy="15" r="15" fill="#E6351E">
                    <animate attributeName="r" from="15" to="15" begin="0s" dur={`${duration}s`} values="15;15;15" calcMode="linear" repeatCount="indefinite"></animate>
                    <animate attributeName="fill-opacity" from="1" to="1" begin="0s" dur={`${duration}s`} values="0;0;0;0;.5;1;1" calcMode="linear" repeatCount="indefinite"></animate>
                </circle>
            </svg>
        </div>
    );
}

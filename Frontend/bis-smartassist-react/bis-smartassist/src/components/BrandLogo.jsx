import React from 'react';
import { BIS_LOGO_BASE64 } from '../utils/logo';

export default function BrandLogo({ size = 30, imgSize = 22 }) {
  return (
    <div className="brand-badge" style={{ width: size, height: size }}>
      <img src={BIS_LOGO_BASE64} alt="BIS Logo" style={{ width: imgSize, height: imgSize }} />
    </div>
  );
}

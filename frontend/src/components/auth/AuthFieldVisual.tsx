"use client";

/** Decorative moisture-colored parcels — not a real map / satellite claim. */
export function AuthFieldVisual() {
  return (
    <div
      className="auth-field-visual relative mb-6 overflow-hidden rounded-2xl border border-white/20 bg-[#0f2a1c]/60 shadow-inner"
      aria-hidden
    >
      <svg
        viewBox="0 0 360 176"
        className="h-44 w-full"
        role="img"
        aria-label="Dekoratif arazi şeması"
      >
        <defs>
          <linearGradient id="authSoil" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#1b4332" />
            <stop offset="55%" stopColor="#2d6a4f" />
            <stop offset="100%" stopColor="#40916c" />
          </linearGradient>
          <filter id="authSoft" x="-10%" y="-10%" width="120%" height="120%">
            <feGaussianBlur stdDeviation="0.6" />
          </filter>
        </defs>

        <rect width="360" height="176" fill="url(#authSoil)" />

        {/* Schematic parcels with moisture tones */}
        <g className="auth-parcel auth-parcel-a" filter="url(#authSoft)">
          <path
            d="M28 36 L132 28 L148 118 L42 128 Z"
            fill="#f59e0b"
            fillOpacity="0.78"
            stroke="rgba(255,255,255,0.45)"
            strokeWidth="1.2"
          />
        </g>
        <g className="auth-parcel auth-parcel-b" filter="url(#authSoft)">
          <path
            d="M142 30 L248 22 L262 108 L154 116 Z"
            fill="#84cc16"
            fillOpacity="0.82"
            stroke="rgba(255,255,255,0.45)"
            strokeWidth="1.2"
          />
        </g>
        <g className="auth-parcel auth-parcel-c" filter="url(#authSoft)">
          <path
            d="M258 24 L338 34 L328 122 L268 110 Z"
            fill="#22c55e"
            fillOpacity="0.8"
            stroke="rgba(255,255,255,0.45)"
            strokeWidth="1.2"
          />
        </g>
        <g className="auth-parcel auth-parcel-d" filter="url(#authSoft)">
          <path
            d="M48 132 L160 122 L172 158 L56 166 Z"
            fill="#fb923c"
            fillOpacity="0.75"
            stroke="rgba(255,255,255,0.4)"
            strokeWidth="1.2"
          />
        </g>
        <g className="auth-parcel auth-parcel-e" filter="url(#authSoft)">
          <path
            d="M168 120 L270 112 L280 154 L178 160 Z"
            fill="#4ade80"
            fillOpacity="0.78"
            stroke="rgba(255,255,255,0.4)"
            strokeWidth="1.2"
          />
        </g>

        {/* Sensor nodes */}
        <circle className="auth-node" cx="88" cy="78" r="4.5" fill="#ecfccb" />
        <circle className="auth-node auth-node-delay" cx="198" cy="68" r="4.5" fill="#ecfccb" />
        <circle className="auth-node" cx="292" cy="72" r="4.5" fill="#ecfccb" />

        {/* Field path */}
        <path
          d="M24 150 C 90 138, 160 152, 220 140 S 320 148, 340 136"
          fill="none"
          stroke="rgba(255,255,255,0.28)"
          strokeWidth="2"
          strokeDasharray="6 5"
        />
      </svg>

      <div className="absolute inset-x-0 bottom-0 flex items-center justify-between gap-2 bg-gradient-to-t from-black/45 to-transparent px-3 pb-2.5 pt-8 text-[10px] font-medium text-white/90">
        <span>Dekoratif arazi şeması · demo twin</span>
        <span className="tabular-nums text-lime-200/90">nem tonları</span>
      </div>
    </div>
  );
}

# HF Virtual Stylist - Design System

**Version:** 1.0.0
**Last Updated:** 2025-10-30
**Inspired By:** [Harris & Frank](https://harrisandfrank.com) luxury menswear aesthetic

---

## Overview

This design system defines the visual language and component patterns for the HF Virtual Stylist admin interface. It emphasizes sophistication, elegance, and minimalism to reflect the Harris & Frank luxury brand identity.

---

## Typography

### Font Families

**Primary (Headers):** Figtree
- Weights: 400 (Regular), 500 (Medium), 600 (Semibold)
- Usage: Page titles, section headers, card titles
- Letter-spacing: `0.2em` for elegant elongation
- Line-height: `1.2`

**Secondary (Body):** Jost
- Weights: 400 (Regular), 500 (Medium), 600 (Semibold)
- Usage: Body text, labels, buttons, descriptions
- Letter-spacing: Normal (`0em`)
- Line-height: `1.6` for readability

### Type Scale

```css
--text-xs: 12px;      /* Captions, helper text */
--text-sm: 14px;      /* Body text (default) */
--text-base: 16px;    /* Emphasized text */
--text-lg: 18px;      /* Subheadings */
--text-xl: 24px;      /* Section titles */
--text-2xl: 32px;     /* Page titles */
--text-3xl: 48px;     /* Hero text */
```

### Usage Examples

```tsx
// Page Title
<h1 className="font-header text-2xl tracking-[0.2em]">
  Familias de Telas
</h1>

// Section Title
<h2 className="font-header text-xl tracking-[0.1em]">
  Imágenes Generadas
</h2>

// Body Text
<p className="font-body text-sm">
  Select a fabric family to view colors.
</p>

// Label
<label className="font-body text-xs uppercase tracking-wide">
  Status
</label>
```

---

## Color Palette

### Primary Colors

```css
--color-dark: #1c1d1d;           /* Primary text */
--color-charcoal: #222222;       /* Secondary text, dark accents */
--color-white: #ffffff;          /* White backgrounds, text on dark */
--color-bg-light: #f9f9f9;       /* Page background */
```

### Neutral Colors

```css
--color-gray-100: #f5f5f5;
--color-gray-200: #e5e5e5;       /* Borders */
--color-gray-300: #d4d4d4;
--color-gray-400: #a3a3a3;
--color-gray-500: #737373;
--color-gray-600: #525252;       /* Muted text */
--color-gray-700: #404040;
--color-gray-800: #262626;
--color-gray-900: #171717;
```

### Status Colors

```css
--color-active: #10b981;         /* Green - Active status */
--color-inactive: #6b7280;       /* Gray - Inactive status */
--color-success: #10b981;        /* Green - Success states */
--color-warning: #f59e0b;        /* Amber - Warning states */
--color-danger: #ef4444;         /* Red - Danger/delete */
--color-info: #3b82f6;           /* Blue - Informational */
```

### Shadows

```css
--shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.05);
--shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.08);
--shadow-md: 0 4px 6px rgba(0, 0, 0, 0.08);
--shadow-lg: 0 8px 16px rgba(0, 0, 0, 0.08);
--shadow-xl: 0 12px 24px rgba(0, 0, 0, 0.12);
--shadow-elevated: 0 4px 12px rgba(0, 0, 0, 0.08);  /* Hover state */
```

### Usage Guidelines

**Text:**
- Primary content: `--color-dark`
- Secondary content: `--color-gray-600`
- Disabled: `--color-gray-400`

**Backgrounds:**
- Page: `--color-bg-light`
- Cards/containers: `--color-white`
- Hover states: `--color-gray-100`

**Borders:**
- Default: `--color-gray-200`
- Focus: `--color-dark`

**Status:**
- Active elements: `--color-active`
- Inactive elements: `--color-inactive`
- Destructive actions: `--color-danger`

---

## Spacing System

### Scale

```css
--spacing-1: 4px;
--spacing-2: 8px;
--spacing-3: 12px;
--spacing-4: 16px;
--spacing-5: 20px;
--spacing-6: 24px;
--spacing-8: 32px;
--spacing-10: 40px;
--spacing-12: 48px;
--spacing-16: 64px;
--spacing-20: 80px;
```

### Semantic Spacing

```css
--spacing-card: 24px;            /* Card padding */
--spacing-section: 64px;         /* Section gaps */
--spacing-grid-gap: 24px;        /* Grid column/row gap */
--max-width: 1200px;             /* Container max-width */
```

### Usage

```tsx
// Card padding
<div className="p-6">  /* 24px */

// Section spacing
<section className="space-y-16">  /* 64px vertical */

// Grid gap
<div className="grid gap-6">  /* 24px */
```

---

## Layout

### Grid System

**Fabric Cards Grid:**
```css
.admin-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--spacing-grid-gap);
  max-width: var(--max-width);
}
```

**Responsive Breakpoints:**
```css
/* Mobile (default) */
.grid { grid-template-columns: 1fr; }

/* Tablet */
@media (min-width: 768px) {
  .grid { grid-template-columns: repeat(2, 1fr); }
}

/* Desktop */
@media (min-width: 1024px) {
  .grid { grid-template-columns: repeat(3, 1fr); }
}

/* Wide Desktop */
@media (min-width: 1280px) {
  .grid { grid-template-columns: repeat(4, 1fr); }
}
```

### Container

```tsx
<div className="max-w-[1200px] mx-auto px-6">
  {children}
</div>
```

---

## Components

### Buttons

#### Primary Button

```tsx
<button className="
  bg-[var(--color-dark)]
  text-white
  px-6 py-3
  rounded-[3px]
  font-body
  text-sm
  transition-transform duration-[280ms] ease-[cubic-bezier(0.2,0.7,0.2,1)]
  hover:translate-y-[-3px]
  hover:shadow-[var(--shadow-elevated)]
  active:translate-y-0
">
  Button Text
</button>
```

**Variants:**
- **Primary:** Dark background, white text
- **Secondary:** White background, dark border, dark text
- **Danger:** Red background, white text
- **Ghost:** Transparent background, dark text, hover background

#### Button Sizes

```tsx
// Small
<button className="px-4 py-2 text-xs">Small</button>

// Medium (default)
<button className="px-6 py-3 text-sm">Medium</button>

// Large
<button className="px-8 py-4 text-base">Large</button>
```

### Cards

#### Basic Card

```tsx
<div className="
  bg-white
  rounded-[3px]
  p-6
  shadow-[var(--shadow-sm)]
  transition-shadow duration-[280ms]
  hover:shadow-[var(--shadow-elevated)]
">
  {content}
</div>
```

#### Fabric Card

```tsx
<div className="bg-white rounded-[3px] overflow-hidden shadow-sm hover:shadow-elevated transition-all group">
  {/* Image Section */}
  <div className="aspect-[4/3] relative">
    <Image src={swatch_url} fill className="object-cover" />
    {/* Overlay on hover */}
    <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity">
      <span className="font-header text-white tracking-[0.2em]">
        {family_name}
      </span>
    </div>
  </div>

  {/* Content Section */}
  <div className="p-6">
    <h3 className="font-header text-lg tracking-[0.1em]">{name}</h3>
    <p className="font-body text-sm text-gray-600">{count} colors</p>
  </div>
</div>
```

### Status Toggle

**Design:** iOS-style switch

```tsx
<button
  className="relative w-12 h-6 rounded-full transition-colors"
  style={{
    backgroundColor: status === "active"
      ? "var(--color-active)"
      : "var(--color-inactive)"
  }}
>
  <span
    className="absolute top-1 w-4 h-4 bg-white rounded-full transition-transform"
    style={{
      transform: status === "active" ? "translateX(28px)" : "translateX(4px)"
    }}
  />
</button>
```

**States:**
- **Active:** Green background, circle on right
- **Inactive:** Gray background, circle on left
- **Hover:** Brightness +10%
- **Disabled:** Opacity 0.5

### Search Bar

```tsx
<div className="relative max-w-md">
  <input
    type="text"
    placeholder="Search fabrics..."
    className="
      w-full
      px-4 py-3 pl-12
      border border-[var(--color-border)]
      rounded-[3px]
      font-body text-sm
      focus:outline-none focus:border-[var(--color-dark)]
      transition-colors
    "
  />
  <SearchIcon className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" />
</div>
```

### Status Badge

```tsx
<span className="
  inline-flex items-center
  px-3 py-1
  rounded-full
  font-body text-xs font-medium
  bg-[var(--color-active)]/10
  text-[var(--color-active)]
">
  Activo
</span>

<span className="
  inline-flex items-center
  px-3 py-1
  rounded-full
  font-body text-xs font-medium
  bg-[var(--color-inactive)]/10
  text-[var(--color-inactive)]
">
  Inactivo
</span>
```

### Image Gallery Grid (Masonry)

```tsx
<div className="columns-1 md:columns-2 lg:columns-3 xl:columns-4 gap-6">
  {images.map(img => (
    <div key={img.id} className="break-inside-avoid mb-6">
      <img
        src={img.url}
        className="w-full rounded-[3px] shadow-sm hover:shadow-lg transition-shadow cursor-pointer"
      />
    </div>
  ))}
</div>
```

---

## Animations & Transitions

### Timing Functions

```css
--ease-smooth: cubic-bezier(0.2, 0.7, 0.2, 1);  /* Luxury hover */
--ease-fast: cubic-bezier(0.4, 0, 0.2, 1);      /* Quick interactions */
--ease-spring: cubic-bezier(0.68, -0.55, 0.265, 1.55);  /* Bounce */
```

### Duration

```css
--duration-fast: 150ms;     /* Toggle states */
--duration-normal: 280ms;   /* Hover effects (luxury) */
--duration-slow: 400ms;     /* Modal animations */
```

### Common Transitions

**Hover Elevation:**
```css
transition: transform 280ms cubic-bezier(0.2, 0.7, 0.2, 1);
hover:transform: translateY(-3px);
hover:box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
```

**Fade In:**
```css
opacity: 0;
animation: fadeIn 280ms ease forwards;

@keyframes fadeIn {
  to { opacity: 1; }
}
```

**Slide Up:**
```css
transform: translateY(20px);
opacity: 0;
animation: slideUp 280ms ease forwards;

@keyframes slideUp {
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
```

---

## Iconography

### Style Guidelines

- **Size:** 20px default (1.25rem)
- **Stroke:** 1.5px
- **Style:** Outline/line icons (not filled)
- **Library:** Heroicons or Lucide React

### Common Icons

```tsx
import {
  MagnifyingGlassIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  PlusIcon,
  XMarkIcon,
  ChevronDownIcon,
  ArrowsRightLeftIcon,
} from "@heroicons/react/24/outline";
```

### Usage

```tsx
<SearchIcon className="w-5 h-5 text-gray-400" />
<EyeIcon className="w-5 h-5 text-gray-600 hover:text-gray-900" />
```

---

## Accessibility

### Focus States

```css
:focus-visible {
  outline: 2px solid var(--color-dark);
  outline-offset: 2px;
}
```

### Color Contrast

- Text on white: Minimum AA (4.5:1) - ✅ `#1c1d1d` passes
- Small text: Minimum AAA (7:1)
- Status colors: Verified for contrast

### Keyboard Navigation

- **Tab:** Navigate between interactive elements
- **Enter/Space:** Activate buttons
- **Escape:** Close modals
- **Arrow keys:** Navigate lists/grids

### Screen Readers

```tsx
<button aria-label="Toggle fabric status">
  <StatusIcon />
</button>

<img src={url} alt="Fabric swatch 095T-0121" />

<div role="status" aria-live="polite">
  Status updated successfully
</div>
```

---

## Responsive Design

### Breakpoints

```css
/* Mobile-first approach */
sm: 640px;   /* Small tablets */
md: 768px;   /* Tablets */
lg: 1024px;  /* Desktops */
xl: 1280px;  /* Large desktops */
2xl: 1536px; /* Wide screens */
```

### Priority

1. **Desktop (1024px+):** Primary optimization target
2. **Tablet (768px-1023px):** Full functionality, 2-column layouts
3. **Mobile (< 768px):** Basic functionality, single column

### Adaptive Components

**Card Grid:**
- Desktop: 3-4 columns
- Tablet: 2 columns
- Mobile: 1 column

**Navigation:**
- Desktop: Horizontal tabs
- Tablet: Horizontal tabs
- Mobile: Dropdown menu

**Modals:**
- Desktop: Centered, max-width 600px
- Tablet: Centered, max-width 500px
- Mobile: Full-screen

---

## Best Practices

### Do's ✅

- Use generous white space (64px section gaps)
- Apply 0.2em letter-spacing to headers
- Use 3px border-radius (sharp, not rounded)
- Implement 280ms transitions for luxury feel
- Display swatch images as primary content
- Keep backgrounds neutral (#f9f9f9, white)
- Use subtle shadows (0.08 alpha)

### Don'ts ❌

- Don't use bright, saturated colors
- Don't use large border-radius (>5px)
- Don't use fast transitions (<150ms for hover)
- Don't prioritize hex colors over images
- Don't add unnecessary animations
- Don't use heavy box-shadows
- Don't use multiple font families

---

## Code Examples

### Luxury Card with Hover

```tsx
<div className="
  bg-white
  rounded-[3px]
  p-6
  shadow-[0_1px_3px_rgba(0,0,0,0.08)]
  transition-all duration-[280ms] ease-[cubic-bezier(0.2,0.7,0.2,1)]
  hover:shadow-[0_4px_12px_rgba(0,0,0,0.08)]
  hover:-translate-y-[3px]
">
  <h3 className="font-[var(--font-figtree)] tracking-[0.1em] text-lg mb-2">
    Card Title
  </h3>
  <p className="font-[var(--font-jost)] text-sm text-[var(--color-gray-600)]">
    Card description with refined readability.
  </p>
</div>
```

### Status Toggle Component

```tsx
"use client";

interface StatusToggleProps {
  status: "active" | "inactive";
  onChange: (status: "active" | "inactive") => void;
  disabled?: boolean;
}

export function StatusToggle({ status, onChange, disabled }: StatusToggleProps) {
  return (
    <button
      onClick={() => onChange(status === "active" ? "inactive" : "active")}
      disabled={disabled}
      className={`
        relative w-12 h-6 rounded-full transition-colors duration-150
        ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
      `}
      style={{
        backgroundColor: status === "active"
          ? "var(--color-active)"
          : "var(--color-inactive)"
      }}
    >
      <span
        className="absolute top-1 w-4 h-4 bg-white rounded-full transition-transform duration-150"
        style={{
          transform: status === "active" ? "translateX(28px)" : "translateX(4px)"
        }}
      />
    </button>
  );
}
```

---

## Resources

- **Fonts:** [Google Fonts - Figtree](https://fonts.google.com/specimen/Figtree), [Jost](https://fonts.google.com/specimen/Jost)
- **Icons:** [Heroicons](https://heroicons.com), [Lucide](https://lucide.dev)
- **Colors:** [ColorHunt](https://colorhunt.co) for palette exploration
- **Inspiration:** [Harris & Frank](https://harrisandfrank.com)

---

**Version History:**
- **1.0.0** (2025-10-30) - Initial design system documentation

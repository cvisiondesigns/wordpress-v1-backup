# Static Site Migration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Migrate the legacy WordPress static export to a modern, maintainable Astro + Tailwind CSS architecture in a new `astro-rebuild` directory.

**Architecture:** 
- **Framework:** Astro (latest)
- **Styling:** Tailwind CSS (via Astro integration)
- **Structure:** `astro-rebuild/` directory for isolation. 1:1 visual replication of existing design.

**Tech Stack:** Astro, Tailwind CSS, NPM

---

### Task 1: Project Initialization & Configuration

**Files:**
- Create: `astro-rebuild/` (directory)
- Create: `astro-rebuild/package.json`
- Create: `astro-rebuild/astro.config.mjs`
- Create: `astro-rebuild/tailwind.config.mjs`

**Step 1.1: Create & Initialize Astro Project**
Run:
```bash
# Create directory
mkdir -p astro-rebuild

# Initialize Astro (using minimal template)
# We use npm create astro@latest but non-interactive
cd astro-rebuild
npm create astro@latest . -- --template minimal --install --no-git --typescript strict
```

**Step 1.2: Install Tailwind CSS**
Run:
```bash
cd astro-rebuild
npx astro add tailwind --yes
```

**Step 1.3: Configure Tailwind Theme (Preliminary)**
Modify `astro-rebuild/tailwind.config.mjs` to include the core colors from the legacy site.
*   Legacy Blue: `#4275f4`
*   Legacy Text: `#545353`
*   Legacy Link: `#05809e`

```javascript
/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
	theme: {
		extend: {
			colors: {
				'legacy-blue': '#4275f4',
				'legacy-text': '#545353',
				'legacy-link': '#05809e',
			},
			fontFamily: {
				// Based on legacy CSS: -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto...
				sans: ['-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', 'Oxygen-Sans', 'Ubuntu', 'Cantarell', '"Helvetica Neue"', 'sans-serif'],
			}
		},
	},
	plugins: [],
}
```

**Step 1.4: Verify Setup**
Run: `npm run build`
Expected: Success.

**Step 1.5: Commit**
```bash
git add astro-rebuild/
git commit -m "chore: init Astro project with Tailwind CSS"
```

---

### Task 2: Global Layout & Assets

**Files:**
- Create: `astro-rebuild/src/styles/global.css`
- Create: `astro-rebuild/src/layouts/MainLayout.astro`
- Copy: Assets from `wp-content/uploads` to `astro-rebuild/public/wp-content/uploads`

**Step 2.1: Asset Migration**
Run:
```bash
# Create target directory structure
mkdir -p astro-rebuild/public/wp-content
# Copy uploads (recursive)
cp -r wp-content/uploads astro-rebuild/public/wp-content/
```

**Step 2.2: Global CSS**
Create `astro-rebuild/src/styles/global.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
    @apply text-legacy-text text-[14px];
}

a {
    @apply text-legacy-link no-underline;
}

h1 {
    @apply text-2xl font-normal m-0;
    font-family: Verdana, Geneva, sans-serif;
}
```

**Step 2.3: Main Layout Component**
Create `astro-rebuild/src/layouts/MainLayout.astro`:
```astro
---
import '../styles/global.css';

interface Props {
	title?: string;
}

const { title = "澄視維度設計 C / Vision Design" } = Astro.props;
---

<html lang="zh-TW">
	<head>
		<meta charset="utf-8" />
		<link rel="icon" type="image/svg+xml" href="/favicon.svg" />
		<meta name="viewport" content="width=device-width, initial-scale=1" />
		<meta name="generator" content={Astro.generator} />
		<title>{title}</title>
	</head>
	<body class="bg-gray-100">
		<slot />
	</body>
</html>
```

**Step 2.4: Commit**
```bash
git add astro-rebuild/src/styles astro-rebuild/src/layouts astro-rebuild/public
git commit -m "feat: add global styles and MainLayout"
```

---

### Task 3: Core Components (Header & Footer)

**Files:**
- Create: `astro-rebuild/src/components/Header.astro`
- Create: `astro-rebuild/src/components/Footer.astro`
- Modify: `astro-rebuild/src/pages/index.astro` (to test components)

**Step 3.1: Header Component**
Create `astro-rebuild/src/components/Header.astro`. *Note: Need to check original HTML index.html for exact structure.*
(Assumption: A simple header with logo and nav)
```astro
---
---
<header class="bg-white border-b border-gray-200">
    <div class="container mx-auto px-4 py-4 flex justify-between items-center">
        <div class="logo">
           <!-- Placeholder for logo structure -->
           <a href="/" class="text-2xl font-bold text-legacy-blue">C / Vision Design</a>
        </div>
        <nav>
            <ul class="flex space-x-6">
                <!-- Placeholder menu items based on analysis later -->
                <li><a href="/" class="hover:text-legacy-blue">Home</a></li>
                <li><a href="/about" class="hover:text-legacy-blue">About</a></li>
                <li><a href="/works" class="hover:text-legacy-blue">Works</a></li>
                <li><a href="/contact" class="hover:text-legacy-blue">Contact</a></li>
            </ul>
        </nav>
    </div>
</header>
```

**Step 3.2: Footer Component**
Create `astro-rebuild/src/components/Footer.astro`.
```astro
---
const year = new Date().getFullYear();
---
<footer class="bg-gray-800 text-white py-8 mt-12">
    <div class="container mx-auto px-4 text-center">
        <p>&copy; {year} 澄視維度設計 C / Vision Design. All rights reserved.</p>
    </div>
</footer>
```

**Step 3.3: Update Index Page**
Modify `astro-rebuild/src/pages/index.astro` to use Layout and Components.
```astro
---
import MainLayout from '../layouts/MainLayout.astro';
import Header from '../components/Header.astro';
import Footer from '../components/Footer.astro';
---

<MainLayout title="Home - 澄視維度設計">
	<Header />
	<main class="container mx-auto px-4 py-8 bg-white my-8 shadow-sm min-h-screen">
		<h1 class="text-3xl font-bold underline text-legacy-blue mb-4">
			Hello world!
		</h1>
        <p>Welcome to the rebuilt site.</p>
	</main>
	<Footer />
</MainLayout>
```

**Step 3.4: Verify**
Run: `npm run dev` (Check localhost manually or rely on build success)
Run: `npm run build`

**Step 3.5: Commit**
```bash
git add astro-rebuild/src/components astro-rebuild/src/pages
git commit -m "feat: add Header and Footer components"
```

---

### Task 4: Content Migration (Homepage)

**Files:**
- Modify: `astro-rebuild/src/pages/index.astro`

**Step 4.1: Analyze Original Homepage**
(I will read the original `index.html` body content in detail during execution)

**Step 4.2: Migrate Content**
Port the HTML content from the original `index.html` into `astro-rebuild/src/pages/index.astro`, replacing:
- `class="..."` with Tailwind equivalents (or keeping them and adding utility classes if 1:1 mapping is hard initially, but goal is Tailwind).
- `<img>` src paths to `/wp-content/...` (already mapped in Task 2).
- Links to internal pages (temporarily dead links or point to `#`).

**Step 4.3: Commit**
```bash
git add astro-rebuild/src/pages/index.astro
git commit -m "feat: migrate homepage content"
```

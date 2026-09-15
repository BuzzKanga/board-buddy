# Board Buddy — Frontend

The frontend for Board Buddy, built with **React 19**, **TanStack Start**, **TanStack Router**, and **Tailwind CSS v4**.

See the main [Project README](../README.md) for full stack setup and architecture details.

---

## Development

### Prerequisites

- **Node.js** (v18+) and **npm**
- The FastAPI backend running on `http://localhost:8000` (see [root README](../README.md#1-start-the-backend))

### Commands

```bash
npm install        # Install dependencies
npm run dev        # Start development server on http://localhost:5173
npm run build      # Build for production with Vite and Nitro
npm run lint       # Lint source code
npm run format     # Format code with Prettier
```

---

## Backend Integration

The frontend client in `src/services/api.ts` connects directly to the FastAPI backend at `http://localhost:8000`. All board mutations, column updates, card changes, and label tags are synced directly to the backend.

---

## Lovable Integration

This UI was originally scaffolded with [Lovable](https://lovable.dev). You can continue developing UI components either directly in code or through the [Lovable editor](https://lovable.dev/projects/b4f181e7-8260-4b2d-8293-54ac144e0813).

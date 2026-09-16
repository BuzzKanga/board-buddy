/**
 * Client-side SPA entry point — used for the Docker production build.
 *
 * This bypasses TanStack Start / Nitro SSR and renders the app as a pure
 * client-side SPA.  All route components are unchanged; only the bootstrap
 * differs.
 */

import "./styles.css";

import ReactDOM from "react-dom/client";
import { RouterProvider } from "@tanstack/react-router";
import { getRouter } from "./router";

const router = getRouter();

ReactDOM.createRoot(document.getElementById("root")!).render(
  <RouterProvider router={router} />,
);

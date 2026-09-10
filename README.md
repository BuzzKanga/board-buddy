# Board Buddy

Build a mini-kanban board web app frontend using React. This is a frontend-only build — use in-memory/localStorage mock services in place of a real backend for now (a real Node/Express + Postgres backend will be connected later, so keep the mock data layer cleanly separated behind functions that mirror REST calls).

CONTEXT
No authentication. Each visitor sets a display name and color on first visit (stored in localStorage), used to identify them as a card assignee. No login, no passwords, no server-verified identity.

CORE ENTITIES
- Board: id, name, created_at
- Column: id, board_id, name, position (belongs to a board, user can rename/reorder/delete)
- Card: id, column_id, title, description, assignee_name, assignee_color, due_date, priority (low/medium/high), position, created_at, updated_at
- Label: id, board_id, name, color (reusable across cards on that board)
- CardLabel: join between cards and labels (many-to-many)

FEATURES TO BUILD
1. Board list/home screen: shows all boards, create new board, open a board, rename/delete a board
2. Board view: shows columns left-to-right, each with its cards stacked vertically
3. Columns: create new column, rename column, delete column (if it has cards, ask for confirmation), drag-and-drop to reorder columns
4. Cards: create card (title required, rest optional), click to open/edit full card details (description, assignee, due date, priority, labels), delete card
5. Drag-and-drop cards within a column to reorder, and across columns to move
6. Labels: create a label (name + color) scoped to the board, attach/remove labels on a card, show label chips on card previews
7. Priority: shown as a visual badge/color on card previews (e.g. low/medium/high)
8. Assignee: pick from a simple list of "known" names/colors (people who have used the app on this browser, or manually entered) — show as a colored avatar/initial on card previews

MOCK SERVICE LAYER
Implement a data access layer (e.g. `services/api.js` or similar) with functions matching this REST shape, backed by localStorage/in-memory state for now:
- getBoards(), createBoard(name), updateBoard(id, data), deleteBoard(id)
- getBoard(id) — returns board with its columns, cards, and labels
- createColumn(boardId, name), updateColumn(id, data), deleteColumn(id)
- createCard(columnId, data), updateCard(id, data) — updateCard handles edits AND moves/reorders (accepts column_id + position), deleteCard(id)
- createLabel(boardId, data), deleteLabel(id)
- attachLabelToCard(cardId, labelId), removeLabelFromCard(cardId, labelId)

Keep every function async (return Promises) even though they're backed by localStorage, so swapping in real fetch() calls later requires no component changes. Seed one sample board with 3 columns (e.g. "To Do", "In Progress", "Done") and a few example cards on first load if no data exists.

REAL-TIME SYNC (future — stub only)
The real app will sync live across users via WebSockets. For this mock build, don't implement real-time — just make sure the mock API layer is the single source of truth components read from, so a live-update layer can be added later without restructuring.

DESIGN
Clean, modern kanban look — clear column headers, card previews with title, priority badge, label chips, assignee avatar, and due date. Responsive for desktop use primarily.

NON-GOALS FOR THIS BUILD
No authentication, no comments/activity history, no file attachments, no notifications, no cross-board search.


Paste this into Lovable as-is. When you're ready to wire up the real backend in Antigravity, the mock layer's function signatures map directly to the REST endpoints in the spec doc, so swapping them out should be mechanical.

This project was built with [Lovable](https://lovable.dev).

## Build with Lovable

Continue developing this project in the [Lovable editor](https://lovable.dev/projects/b4f181e7-8260-4b2d-8293-54ac144e0813).

- **Ship faster**: describe what you want to build and Lovable handles the code.
- **Stay in sync**: every change made in Lovable is committed straight to this repository.
- **Full ownership**: this code is yours. Push to `main` on GitHub and your changes sync back into Lovable, ready for your next prompt.

## Development

Prefer working locally? You need Node.js and npm — [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating).

```sh
git clone <this-repository-url>
cd <repository-name>
npm i
npm run dev
```

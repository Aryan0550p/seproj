# Backend Logic Snapshot

This folder contains backend-style business logic extracted for mentor review.

## Persistence
- The backend now persists data in a SQLite database file: `backend/yumsie.db`.
- Existing `backend/data.json` is used only as a one-time migration source if present.
- After migration, all reads and writes go through SQLite.

## Included file
- `store.js`: Core logic implemented during this phase:
  - Activity logging mechanism
  - Discrepancy alert and notification generation
  - Order completion verification
  - Stock validation and stock adjustment workflows
  - Dispatch/cancel inventory updates
  - Pending payment calculations

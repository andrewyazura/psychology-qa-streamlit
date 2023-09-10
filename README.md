---
title: Psychology Q&A
emoji: 🧠
colorFrom: blue
colorTo: pink
sdk: docker
app_port: 8501
---

# Psychology Q&A

## Database setup

Add `pgvector` extension before creating tables:

```sql
CREATE EXTENSION vector;
```

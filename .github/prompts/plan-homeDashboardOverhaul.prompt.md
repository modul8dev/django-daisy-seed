## Plan: Home Dashboard Overhaul

Replace the placeholder home page with a rich dashboard showing quick actions, draft posts, scheduled posts, async AI inspiration cards, product previews, and conditional CTA blocks. Performance snapshot is excluded for now; AI suggestions are merged into the inspiration cards.

**Decisions**
- Performance snapshot: excluded (no analytics model yet)
- AI Suggestions section: merged into Inspiration cards
- Inspiration cards: pre-generated via a separate async request after page load (avoids blocking initial render)

---

### Phase 1: Home View Context
**File: [webapp/home/views.py](webapp/home/views.py)**

1. Add `@login_required` (currently missing) and import `SocialMediaPost`, `Brand`, `ImageGroup`
2. Build context for `home()`:
   - `drafts` — 4 most recent draft posts (`status='draft'`, ordered by `-updated_at`)
   - `scheduled_posts` — posts scheduled within the current week
   - `brand` / `has_brand` — for CTA visibility, using `Brand.has_data`
   - `products` — 6 random product `ImageGroup`s (with prefetched images)
   - `image_groups` — 6 recent manual groups
   - `has_products` — flag for CTA visibility

### Phase 2: Inspiration Cards Endpoint
**Files: [webapp/home/views.py](webapp/home/views.py), [webapp/home/urls.py](webapp/home/urls.py)**

3. New view `inspiration_cards(request)` — picks 3 random product groups, calls `suggest_topic()` from `social_media.ai_services`, pairs products with topics, renders partial template
4. Add route `path("inspiration/", ...)` to [home/urls.py](webapp/home/urls.py)
5. Graceful fallback if AI fails or no products exist

### Phase 3: Post Create Prefill Support
**File: [webapp/social_media/views.py](webapp/social_media/views.py)**

6. Modify `post_create` GET handler to accept optional query params: `topic`, `seed_image_ids` (comma-separated), `mode=ai`
7. Pass these to template context so Alpine starts in AI mode with pre-selected seed images and topic

### Phase 4: Dashboard Template
**File: [webapp/home/templates/home/home.html](webapp/home/templates/home/home.html)** (rewrite)

Layout sections in order:

| Section | Content | Visibility |
|---|---|---|
| **Quick Actions** | "Create Post" (modal), "Import Products", "Set up Brand" | Always (brand CTA conditional) |
| **Continue Where You Left Off** | Draft post cards — title, image thumb, date, click→edit modal | Only if drafts exist |
| **Scheduled This Week** | Scheduled post cards — title, date/time, platforms | Only if scheduled posts exist |
| **Inspiration (AI Cards)** | Skeleton placeholders, loaded async from `/inspiration/` | Always attempted |
| **Products / Image Groups** | Product cards reusing pattern from [image_group_grid.html](webapp/media_library/templates/media_library/image_group_grid.html) | Only if products exist |
| **CTA Blocks** | "Set up your brand" / "Import your products" banners | Conditional on missing data |

### Phase 5: Async Inspiration Loading
**New file: [webapp/home/templates/home/_inspiration_cards.html](webapp/home/templates/home/_inspiration_cards.html)**

8. Use Unpoly `up-defer="lazy"` with `up-href="{% url 'inspiration_cards' %}"` — loads after page paint, shows skeleton cards while loading
9. Each inspiration card shows: product image, AI topic, "Create Post" button that opens post create modal with `?mode=ai&topic=...&seed_image_ids=...`

---

**Relevant files to modify:**
- [webapp/home/views.py](webapp/home/views.py) — main dashboard context + inspiration endpoint
- [webapp/home/urls.py](webapp/home/urls.py) — add inspiration route
- [webapp/home/templates/home/home.html](webapp/home/templates/home/home.html) — full template rewrite
- [webapp/home/templates/home/_inspiration_cards.html](webapp/home/templates/home/_inspiration_cards.html) — new async partial
- [webapp/social_media/views.py](webapp/social_media/views.py) — query param prefill support for post create

**Key references (read-only):**
- `SocialMediaPost` model: `status`, `scheduled_at`, `updated_at`, `title`, `topic` fields
- `Brand.has_data` property in [brand/models.py](webapp/brand/models.py)
- `suggest_topic(brand, seed_images)` in [social_media/ai_services.py](webapp/social_media/ai_services.py)
- Card UI pattern in [image_group_grid.html](webapp/media_library/templates/media_library/image_group_grid.html)

**Verification**
1. Home page loads with all sections, proper Tailwind/DaisyUI layout
2. Drafts show only user's drafts (max 4), clicking opens edit modal
3. Scheduled shows only current-week posts, clicking opens edit modal
4. CTA blocks appear when brand/products missing, hidden otherwise
5. Inspiration cards load async (visible in network tab as `/inspiration/`)
6. Clicking inspiration card opens post create modal in AI mode with topic + seed images prefilled
7. Empty-state user (no posts/products) sees CTAs and clean layout, no errors
8. AI failure in inspiration → graceful fallback (empty or retry prompt)

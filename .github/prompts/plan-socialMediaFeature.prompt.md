# Plan: Social Media Post Composer

Build a `social_media` Django app with a single-modal tabbed composer for multi-platform posts. Shared content lives at the post level; per-platform overrides are opt-in. Follows existing FBV + Unpoly patterns from the `media_library` app.

---

## Phase 1: Data Layer (Steps 1–7)

1. **Create the app** — `python manage.py startapp social_media` from `webapp/`, register in `INSTALLED_APPS` in `webapp/core/settings.py`
2. **`SocialMediaSettings` model** — OneToOneField to `AUTH_USER_MODEL` with `enable_linkedin`, `enable_x`, `enable_facebook`, `enable_instagram` booleans (all default `False`). Helper method `get_enabled_platforms()` returns list of enabled platform keys. Lives in the new app, not on `CustomUser`.
3. **`SocialMediaPost` model** — `user` (FK), `title`, `shared_text`, `status` (draft/scheduled/published/failed), `scheduled_at`, `published_at`, `created_at`, `updated_at`. Meta: `ordering = ['-created_at']`
4. **`SocialMediaPostPlatform` model** — FK to post, `platform` choice field, `is_enabled`, `use_shared_text` (default True), `override_text`, `use_shared_media` (default True). `unique_together = [('post', 'platform')]`. Methods: `get_effective_text()`, `get_effective_media()`
5. **`SocialMediaPostMedia` model** (shared media) — FK to post (related_name `shared_media`), FK to `media_library.Image`, `sort_order`
6. **`SocialMediaPlatformMedia` model** (override media) — FK to platform variant (related_name `override_media`), FK to `media_library.Image`, `sort_order`
7. **Migrations + admin** — `makemigrations`, `migrate`, register models with inline admin for platform variants

---

## Phase 2: User Platform Settings UI (Steps 8–9)

8. **`SocialMediaSettingsForm`** — ModelForm in `webapp/social_media/forms.py` with the four enable checkboxes, DaisyUI checkbox styling
9. **Add to Settings page** — Update `webapp/home/templates/home/settings.html` with a new "Social Media Platforms" card section below the password card. Update `webapp/home/views.py` `settings()` view to `get_or_create` `SocialMediaSettings` and handle both forms on POST.

---

## Phase 3: Post List Page & Navigation (Steps 10–12)

10. **Sidebar nav item** — Add "Social Media" link in `webapp/templates/base.html` sidebar under "Main" section (after Media Library), using same `up-follow` / `menu-active` pattern, pointing to `/social-media/`
11. **URL routing** — New `webapp/social_media/urls.py` with `app_name='social_media'`, routes for list/create/edit/delete. Include from `webapp/core/urls.py` as `path('social-media/', include('social_media.urls'))`
12. **List view + template** — FBV `post_list()` with `@login_required`. Template shows post cards with title, status badge, platform indicators, dates, edit/delete buttons. "Create new post" button triggers Unpoly large modal. Pattern follows `media_library/image_group_list.html`.

---

## Phase 4: Post Composer Modal (Steps 13–17) — *core feature*

13. **Forms** — `SocialMediaPostForm` (title, shared_text, scheduled_at) + `SocialMediaPostPlatformForm` inline formset via `inlineformset_factory` with `extra=0, can_delete=False`
14. **Create/edit views** — On create: read user's enabled platforms, build formset with one initial row per platform. On POST: save post + platform variants + media. Return 204 with `X-Up-Accept-Layer`. Edit: same pattern with existing instances. Delete: POST-only with `X-Up-Events` for list refresh.
15. **Modal template** (`post_form.html`) — Standalone `<main>` (no extends, loaded in Unpoly layer):
    - **Sticky header**: title, Save Draft, Schedule, Cancel
    - **Left column (editor)**: Tab bar ("All Platforms" + per-platform tabs), shared content fields on "All" tab, override toggles + fields on platform tabs
    - **Right column (preview)**: Live preview card, character count, image count, warnings, schedule picker
    - Tab switching is pure client-side show/hide (no server round-trips)
16. **Shared media picker** — Select from existing media_library images or upload new. Inline formset for `SocialMediaPostMedia`. Similar pattern to `image_group_form.html` image rows.
17. **Platform override media picker** — Same component, shown only when "Use shared media" unchecked. On first uncheck, JS prefills from shared images (one-time copy).

---

## Phase 5: Client-Side Behavior (Steps 18–19)

18. **`social_media.js`** in `webapp/static/js/` — Uses `up.compiler()` pattern (required by project convention). Handles:
    - Tab switching (show/hide panels, update preview)
    - Override text toggle: uncheck → show textarea prefilled with current shared text (one-time copy); re-check → hide but don't clear
    - Override media toggle: same pattern
    - Live preview: update right column based on effective values as user types
    - Character count per platform (X: 280, LinkedIn: ~3000, etc.) + warnings
    - Image count + platform-specific limit warnings
19. **Include in base.html** — Add `<script>` tag alongside existing `media_library.js` (compilers must be in base template per project rules)

---

## Phase 6: Media Integration (Step 20)

20. **Image picker component** — Grid of user's existing `media_library.Image` records with selection checkboxes + "upload new" option. Reuses existing media library images via FK — no duplicate uploads.

---

## Relevant Files

### Modify
- `webapp/core/settings.py` — add to INSTALLED_APPS
- `webapp/core/urls.py` — include social_media URLs
- `webapp/templates/base.html` — sidebar nav item + JS include
- `webapp/home/views.py` — settings view handles SocialMediaSettingsForm
- `webapp/home/templates/home/settings.html` — platform checkboxes card

### Create
- `webapp/social_media/` — full app: models, forms, views, urls, admin, templates
- `webapp/social_media/templates/social_media/post_list.html`
- `webapp/social_media/templates/social_media/post_form.html`
- `webapp/static/js/social_media.js`

### Reference (patterns to follow)
- `webapp/media_library/views.py` — `_accept_layer_response()`, formset handling, `@login_required` + user scoping
- `webapp/media_library/templates/media_library/image_group_list.html` — list page with Unpoly modal triggers
- `webapp/media_library/templates/media_library/image_group_form.html` — modal form structure with `up-submit`, `up-layer="current"`
- `webapp/static/js/media_library.js` — `up.compiler()` pattern

---

## Verification

1. Migrations create and apply cleanly
2. `/settings` shows platform checkboxes that persist on save
3. Sidebar shows "Social Media" with active highlighting on `/social-media/`
4. List page renders empty state + "Create new post" button
5. Modal opens at large size showing only enabled platforms as tabs
6. Shared text appears in preview for all platforms
7. Override toggle shows prefilled textarea, toggling back hides it without clearing
8. Same for media overrides
9. Save creates correct `SocialMediaPost` + `SocialMediaPostPlatform` rows in DB
10. Edit reopens modal with saved data intact
11. Delete removes post from list

---

## Decisions

- **Separate settings model** over booleans on `CustomUser` — cleaner separation, room for future social settings
- **FK to `media_library.Image`** for media attachments — reuses existing images, avoids duplication
- **Historical platform rows preserved** — existing posts keep their platform rows even if user disables a platform later; only new posts use current settings
- **No actual publishing in v1** — content modeling and editing workflow only
- **Client-side tab switching** — pure JS show/hide, no server round-trips per tab
- **Override text prefill is one-time** — copies shared text on first toggle to override; subsequent toggles don't re-copy
- **Platform formset approach** — rows are pre-created in the view from enabled platforms (not dynamically added by user in the form)

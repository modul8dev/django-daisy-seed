/* ── Social Media Post Composer ── */

document.addEventListener('alpine:init', () => {
  'use strict';

  Alpine.data('postComposer', () => ({
    PLATFORM_LIMITS: {
      linkedin: 3000,
      x: 280,
      facebook: 63206,
      instagram: 2200,
    },

    activeTab: 'all',
    sharedText: '',
    overrideTextShown: {},
    overrideMediaShown: {},
    overrideText: {},
    textPrefilled: {},

    // ── Lifecycle ─────────────────────────────────────────────────────────

    init() {
      const ta = this.$el.querySelector('#id_shared_text');
      if (ta) this.sharedText = ta.value;

      this.$el.querySelectorAll('[id^="panel-"]:not(#panel-all)').forEach(panel => {
        const platform = panel.id.replace('panel-', '');
        const textToggle = panel.querySelector('.use-shared-text-toggle');
        const mediaToggle = panel.querySelector('.use-shared-media-toggle');
        const overrideField = panel.querySelector('.override-text-field');

        this.overrideTextShown[platform] = textToggle ? !textToggle.checked : false;
        this.overrideMediaShown[platform] = mediaToggle ? !mediaToggle.checked : false;
        this.overrideText[platform] = overrideField ? overrideField.value : '';
        this.textPrefilled[platform] = !!(overrideField && overrideField.value);
      });
    },

    // ── Tab management ────────────────────────────────────────────────────

    activateTab(tab) {
      this.activeTab = tab;
    },

    // ── Preview ───────────────────────────────────────────────────────────

    previewLabel() {
      if (this.activeTab === 'all') return 'All Platforms';
      const btn = this.$el.querySelector(`.tab-btn[data-tab="${this.activeTab}"]`);
      return btn ? btn.textContent.trim() : this.activeTab;
    },

    previewText() {
      const text = this.effectiveText(this.activeTab);
      return text || 'Write something above to see a preview\u2026';
    },

    // ── Text helpers ──────────────────────────────────────────────────────

    effectiveText(platform) {
      if (!platform || platform === 'all') return this.sharedText;
      if (this.overrideTextShown[platform]) return this.overrideText[platform] || '';
      return this.sharedText;
    },

    sharedCharCountLabel() {
      return this.sharedText.length + ' characters';
    },

    // ── Character counting ────────────────────────────────────────────────

    charCount(platform) {
      return this.effectiveText(platform).length;
    },

    charCountLabel(platform) {
      const limit = this.PLATFORM_LIMITS[platform] || 0;
      return this.charCount(platform) + ' / ' + limit;
    },

    charBarWidth(platform) {
      const count = this.charCount(platform);
      const limit = this.PLATFORM_LIMITS[platform] || 1;
      return Math.min((count / limit) * 100, 100) + '%';
    },

    charBarClass(platform) {
      const count = this.charCount(platform);
      const limit = this.PLATFORM_LIMITS[platform] || 0;
      if (count > limit) return 'bg-red-500';
      if (count > limit * 0.8) return 'bg-amber-400';
      return 'bg-emerald-400';
    },

    isOverLimit(platform) {
      const limit = this.PLATFORM_LIMITS[platform] || 0;
      return this.charCount(platform) > limit;
    },

    overLimitBy(platform) {
      const limit = this.PLATFORM_LIMITS[platform] || 0;
      return this.charCount(platform) - limit;
    },

    // ── Override text toggle ──────────────────────────────────────────────

    onSharedTextToggle(platform, event) {
      const checked = event.target.checked;
      if (!checked && !this.textPrefilled[platform] && !this.overrideText[platform]) {
        this.overrideText[platform] = this.sharedText;
        this.textPrefilled[platform] = true;
        // Sync value into the hidden field so Django form submission picks it up
        this.$nextTick(() => {
          const panel = this.$el.querySelector('#panel-' + platform);
          if (panel) {
            const field = panel.querySelector('.override-text-field');
            if (field) field.value = this.overrideText[platform];
          }
        });
      }
      this.overrideTextShown[platform] = !checked;
    },

    // ── Shared media add/remove ───────────────────────────────────────────

    addSharedMedia() {
      const template = this.$el.querySelector('#shared-media-empty');
      const container = this.$el.querySelector('#shared-media-container');
      const totalInput = this.$el.querySelector('[name$="media-TOTAL_FORMS"]');
      if (!template || !container || !totalInput) return;

      const idx = parseInt(totalInput.value, 10);
      const clone = template.content.cloneNode(true);
      clone.querySelectorAll('[name],[id],[for]').forEach(el => {
        ['name', 'id', 'for'].forEach(attr => {
          const val = el.getAttribute(attr);
          if (val) el.setAttribute(attr, val.replace(/__prefix__/g, idx));
        });
      });
      container.appendChild(clone);
      totalInput.value = idx + 1;
    },

    removeSharedMedia(btn) {
      const row = btn.closest('.shared-media-row');
      const totalInput = this.$el.querySelector('[name$="media-TOTAL_FORMS"]');
      if (row && totalInput) {
        row.remove();
        totalInput.value = parseInt(totalInput.value, 10) - 1;
      }
    },
  }));
});

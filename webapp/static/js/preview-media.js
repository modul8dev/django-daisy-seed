class PreviewMedia extends HTMLElement {
    connectedCallback() {
        if (this.dataset.initialized === "true") return;
        this.dataset.initialized = "true";
        this.style.display = "inline-block";

        this.render();
    }

    static get observedAttributes() {
        return ["src", "alt", "class", "style", "data-is-video"];
    }

    attributeChangedCallback() {
        if (this.dataset.initialized === "true") {
            this.render();
        }
    }

    _isVideo() {
        // Explicit attribute takes precedence
        const attr = this.getAttribute("data-is-video");
        if (attr === "true") return true;
        if (attr === "false") return false;
        // Auto-detect from src extension
        const src = this.getAttribute("src") || "";
        return /\.(mp4|mov|avi|webm|mkv|m4v|wmv)(\?|$)/i.test(src);
    }

    render() {
        const src = this.getAttribute("src") || "";
        const alt = this.getAttribute("alt") || "";
        const cls = this.getAttribute("class") || "";
        const style = this.getAttribute("style") || "";
        const isVideo = this._isVideo();

        this.innerHTML = "";

        if (isVideo) {
            const wrapper = document.createElement("div");
            wrapper.className = `${cls} relative cursor-pointer`;
            if (style) wrapper.style.cssText = style;

            const video = document.createElement("video");
            video.src = src;
            video.className = "w-full h-full object-cover";
            video.muted = true;
            video.preload = "metadata";

            const overlay = document.createElement("div");
            overlay.className = "absolute inset-0 flex items-center justify-center pointer-events-none";
            overlay.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="size-8 text-white drop-shadow-lg" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>`;

            wrapper.appendChild(video);
            wrapper.appendChild(overlay);

            wrapper.addEventListener("click", () => {
                PreviewMedia.openPreview(src, alt, true);
            });

            this.appendChild(wrapper);
        } else {
            const img = document.createElement("img");
            img.src = src;
            img.alt = alt;
            img.className = `${cls} cursor-pointer`;
            img.loading = "lazy";
            if (style) img.style.cssText = style;

            img.addEventListener("click", () => {
                PreviewMedia.openPreview(src, alt, false);
            });

            this.appendChild(img);
        }
    }

    static ensureModal() {
        let modal = document.getElementById("preview-media-modal");
        if (modal) return modal;

        modal = document.createElement("div");
        modal.id = "preview-media-modal";
        modal.className = "fixed inset-0 z-[9999] hidden items-center justify-center bg-black/80 p-4";

        modal.innerHTML = `
            <button
                type="button"
                aria-label="Close preview"
                class="absolute right-4 top-4 rounded-full bg-white/10 px-3 py-2 text-white hover:bg-white/20"
            >
                ✕
            </button>
            <img
                class="preview-media-el max-h-[90vh] max-w-[90vw] rounded-lg shadow-2xl object-contain"
                alt=""
            >
            <video
                class="preview-video-el max-h-[90vh] max-w-[90vw] rounded-lg shadow-2xl object-contain hidden"
                controls
                playsinline
            ></video>
        `;

        const close = () => {
            modal.classList.add("hidden");
            modal.classList.remove("flex");
            // Pause video when closing
            const vid = modal.querySelector(".preview-video-el");
            if (vid) vid.pause();
        };

        modal.addEventListener("click", close);

        const button = modal.querySelector("button");
        button.addEventListener("click", (e) => {
            e.stopPropagation();
            close();
        });

        const previewImg = modal.querySelector(".preview-media-el");
        previewImg.addEventListener("click", (e) => { e.stopPropagation(); });

        const previewVid = modal.querySelector(".preview-video-el");
        previewVid.addEventListener("click", (e) => { e.stopPropagation(); });

        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && !modal.classList.contains("hidden")) {
                close();
            }
        });

        document.body.appendChild(modal);
        return modal;
    }

    static openPreview(src, alt = "", isVideo = false) {
        const modal = PreviewMedia.ensureModal();
        const previewImg = modal.querySelector(".preview-media-el");
        const previewVid = modal.querySelector(".preview-video-el");

        if (isVideo) {
            previewImg.classList.add("hidden");
            previewVid.classList.remove("hidden");
            previewVid.src = src;
            previewVid.play();
        } else {
            previewVid.classList.add("hidden");
            previewVid.src = "";
            previewImg.classList.remove("hidden");
            previewImg.src = src;
            previewImg.alt = alt;
        }

        modal.classList.remove("hidden");
        modal.classList.add("flex");
    }
}


customElements.define("preview-media", PreviewMedia);

PRODUCT_IMAGE_PRE_PROMPT = """
Create a prompt for a photorealistic Instagram image featuring one or more e-commerce product(s) in a real-world setting.

Brand info:
{brand_info}

Product info:
{product_info}

Theme / Objective:
{topic}

⸻

General Guidelines:
    •   The image should be perceived as a photograph taken by a professional photographer, so don't put any extra layers of creativity that would make it look like an illustration or a digital art.
    •   Use original props, environments, and lighting — do not copy reference images.
    •   Do not describe the product(s); visuals are provided separately.
    •   If one product → make it the main focus.
    •   If multiple products → show them together naturally in a cohesive, realistic composition.
    •   Each product must be fully visible and clearly recognizable.
    •   The product(s) must be identical to the reference in shape, material, color, texture, and reflection.
        •   Everything else — lighting, background, text, or layout — must be reimagined creatively.
    •   Do not add logos or write any text in the image.
    •   Output only the prompt without any unrelated information (e.g., "here is your prompt").

Safety Guidelines:
    •   Always comply with content policies.
    •   Avoid adult, violent, political, or hateful content.
    •   Depict people respectfully.
    •   Keep all visuals brand-safe, positive, and suitable for public audiences.
"""

LIFESTYLE_IMAGE_PRE_PROMPT = """
Create a prompt for a photorealistic Instagram image that shows one or more e-commerce product(s) in a real-world lifestyle setting.
The image should feel human, emotional, and authentic — where people, environment, and mood tell the story of the product.

Brand info:
{brand_info}

Product info:
{product_info}

Theme / Objective:
{topic}

⸻

General Guidelines:
    •   The image should be perceived as a photograph taken by a professional photographer, so don't put any extra layers of creativity that would make it look like an illustration or a digital art.
    •   The scene should include people naturally wearing, using, or interacting with the product(s) but multiple people should never wear the same product in case of apparel.
    •   Capture genuine unstaged emotion, expression, and atmosphere.
    •   Do not copy or reuse any reference image, model, pose, or location.
    •   If there are people in the image, briefly describe how they look.
    •   Do not describe the product(s); they are provided separately.
    •   If one product → focus on how it's used or worn.
    •   If multiple products → show them together naturally within the same lifestyle moment.
    •   The product(s) must appear identical to the reference in shape, color, material, texture, and reflection.
        •   Everything else — models, lighting, background, text, or layout — must be reimagined creatively.
    •   Do not add logos or write any text in the image.
    •   Output only the prompt without any unrelated information (e.g., "here is your prompt").

Safety Guidelines:
    •   Always comply with content policies.
    •   Avoid adult, violent, political, or hateful content.
    •   Depict people respectfully and inclusively.
    •   Keep all visuals brand-safe, positive, and suitable for public audiences.
"""

AD_IMAGE_PRE_PROMPT = """
Create a prompt for a photorealistic Ad image that features one or more e-commerce product(s) in a real-world setting.
The image should instantly attract attention and communicate the brand's essence and product value.

Brand info:
{brand_info}

Product info:
{product_info}

Theme / Objective:
{topic}

⸻

Creative Direction:
    •   Design a scroll-stopping, emotionally engaging image that feels like a premium DTC ad.
    •   Focus on emotion, storytelling, and brand personality, not sterile product photography.
    •   Use the brand's tone, color palette, and style to define lighting, mood, and composition.
    •   Capture the feeling or benefit the audience should associate with the product.
    •   Do not describe the product(s); their visuals are provided separately.

⸻

Scene & Framing:
    •   The product must be the hero, clearly visible, and instantly recognizable.
    •   Adjust framing by product type:
        •   Wearables / accessories: naturally worn or held by the model.
        •   Lifestyle / tech / home products: placed in an authentic real-world environment.
        •   Small / handheld items: close-up or macro shot with environmental context.
        •   Apparel: half- or full-body shot showing fit and texture.
    •   Lighting should naturally draw attention to the main product.
    •   Avoid awkward crops or unnatural poses.
    •   If there are people in the image, briefly describe how they look.

⸻

Ad Composition & Visual Style:
    •   The image should look publication-ready, like a high-performing social media ad.
    •   Integrate subtle brand elements such as:
        •   Brand-colored gradients, shapes, or textures that enhance composition.
        •   A small, tasteful logo placement (e.g., bottom-right corner).
    •   Maintain a strong visual hierarchy — the product remains the hero.

⸻

Text Overlay:
    •   Short, clear value statement
    •   2–6 words max
    •   Large, readable, high contrast
    •   Uses brand font or a clean sans-serif

⸻

Marketing Context:
    •   Evoke feelings such as curiosity, inspiration, confidence, or joy.
    •   Communicate why the product matters or what experience it enhances.
    •   Keep the visual tone aspirational but believable, avoiding overused ad clichés.

⸻

Visual Fidelity:
    •   The product(s) must appear identical to the reference in shape, color, material, texture, and reflection.
    •   Everything else — models, lighting, background, text, or layout — must be reimagined creatively.

⸻

Safety Guidelines:
    •   Always comply with content policies.
    •   Avoid adult, violent, political, or hateful content.
    •   Depict people respectfully and inclusively.
    •   Keep all visuals brand-safe, positive, and suitable for public audiences.

⸻

Instruction:
Describe exactly what should appear in the final image, including any tagline or logo placement (no variants or drafts).
Output only the prompt without any unrelated information (e.g., "here is your prompt").
"""

IMAGE_VISUAL_FIDELITY_SUFFIX = """

*** Visual Fidelity: *** (UPMOST IMPORTANCE)
- The product(s) in the final image must be visually *identical* to the one(s) in the reference image(s) in terms of shape, material, color, reflections, and texture.
- Everything else — models, lighting, background, text, or layout — must be reimagined creatively.
"""

IMAGE_TYPOGRAPHY_SUFFIX = """

*** Typography: ***
- Do not add logos or write any text in the image.
"""

IMAGE_PRE_PROMPTS = {
    'product': PRODUCT_IMAGE_PRE_PROMPT,
    'lifestyle': LIFESTYLE_IMAGE_PRE_PROMPT,
    'ad': AD_IMAGE_PRE_PROMPT,
}

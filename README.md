# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain
The domain that my system covers would be the food choices around California State University, Fullerton. This knowledge is valuable as it provides students a quick way to easily view food choices around CSUF without the need to sift through various sources online. 
<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 |Reddit: r/csuf|Subreddit of CSUF students discussing potential food spots|https://www.reddit.com/r/csuf/comments/txtiw6/good_places_to_eat_around_csuf/|
| 2 |Titan Eats|Menu of Titan Dining Hall (Gastronome)|https://dineoncampus.com/CSUF/whats-on-the-menu/titan-dining-hall/2026-05-13/breakfast|
| 3 |Yelp|Yelp Top 10 Restaurants near CSUF|https://www.yelp.com/search?cflt=restaurants&find_near=california-state-university-fullerton-fullerton-3|
| 4 |Associated Students Inc: CSUF|Blog Posting from ASI CSUF|https://asi.fullerton.edu/2026/03/23/must-try-spots-to-catch-the-fullerton-vibe-according-to-csuf-students/|
| 5 |The Orange County Register|Newspaper Article Ranking Places|https://www.ocregister.com/2015/04/15/10-great-places-to-eat-on-and-off-the-cal-state-fullerton-campus/|
| 6 |GrubHub|List detailing close-by restaurants|https://www.grubhub.com/delivery/ca-fullerton/california_state_university_fullerton|
| 7 |Daily Titan|Article for new food places|https://dailytitan.com/news/campus/new-food-businesses-near-csuf-welcome-students/article_efb33e88-1042-11ec-9694-637f953bef4a.html|
| 8 |Yelp|Yelp Review Page of CSUF's Gastronome|https://www.yelp.com/biz/the-gastronome-fullerton|
| 9 |Titan Eats|CSUF Titan Dining Hall Info Page|https://dineoncampus.com/CSUF/the-titan-dining-hall|
| 10 |Fullerton.edu|Pricing for CSUF Dining Plan|https://www.fullerton.edu/Housing/current-students/payment-information.html|

---

## Chunking Strategy
Looking at the sources, the majority of these sources include short reviews of each food spot. These reviews include the type of cuisine, the location, and a short description of what the place has to offer. Because of this, the most suitable chunking strategy would be fixed since each of the reviews are relatively the same size in terms of length. 
<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:**
Since we are using fixed size chunking, the chunk size would be around 512 tokens or roughly 350-400 words. This allows enough context to be included within each chunk but also prevents unneccessary and unrelated details to be included with each chunk.
**Overlap:**
The overlap found would be around 50-75 characters. This allows each chunk to have a decent amount of extra characters to capture enough context before being cut off. 
**Why these choices fit your documents:**
I believe these choices fit my documents as my documents are not incredibly dense in information. This means that each chunk could be cut a little short and the meaning of the chunk will remain the same. 
**Final chunk count:**
The final chunk total is 13. This number is a little low because of my web scraper not being able to scrape dynamic content found on certain websites. 
---

## Embedding Model
The embedding model used for this is all-MiniLM-L6-v2. This was chosen of its fast lightweight nature. If this were to be deployed to real users and cost wasn't a constraint, then a different model such as OpenAI text-embedding-3-large could be used as it is considered to be the best overall general-purpose model being able to perform all sorts of tasks while being cost efficient.
<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**
The embedding model used for this is all-MiniLM-L6-v2. This model was recommended by CodePath as it is very cost efficient for the amount of performance it provides. 
**Production tradeoff reflection:**

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

**How source attribution is surfaced in the response:**

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**
Implementing the chunking strategy
- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

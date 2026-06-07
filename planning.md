# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
Student experiences with California State University's dining options - including dining halls, campus cafes, food trucks, and nearby restaurants - vary widely as official sources may not be able to capture food quality, value, hours of operation, and local hidden gems known specifically by CSUF students.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

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

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**

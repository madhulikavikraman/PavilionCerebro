// Self-paced walkthrough: one real screenshot + one plain-English idea per screen.
// Images in img/ are real screenshots of the real dashboard, captured by
// scripts/capture_walkthrough.py from an actual run of the actual swarm — nothing here
// is drawn separately from the product or invented for this page.
"use strict";

const SLIDES = [
  {
    img: null,
    kicker: "Pavilion Cerebro, slowly",
    headline: "One building. Four AI watchers. One brain.",
    body: "This walkthrough is the same real product as the live dashboard, just paused so you can go at your own pace. Every picture ahead is a real screenshot of the real system running on real public data — nothing is mocked up.",
    foot: "Use Next below, or the arrow keys.",
  },
  {
    img: "healthy.jpg",
    kicker: "The big picture",
    headline: "One score for the whole building.",
    body: "This number (0–100) is what a building manager glances at each morning. It drops when any one of the systems below starts looking bad — and it drops faster for dangerous problems (like a battery fire risk) than for minor ones (like a small crack).",
  },
  {
    img: "map.jpg",
    kicker: "How it's wired together",
    headline: "Four watchers, one coordinator.",
    body: "Each dot is one thing being watched — a chiller, a wall, a battery. Every dot reports back to the one brain in the middle. Color tells you how worried to be: green is fine, red is urgent. The dashed shapes are systems we've planned for but haven't built yet.",
  },
  {
    img: "agent0.jpg",
    kicker: "Watcher #1 — Structural Visual",
    headline: "A camera, looking for cracks.",
    body: "This one watches photos of concrete and walls for cracks. The number is how sure it is: 0 means “definitely fine,” 1 means “definitely a crack.”",
  },
  {
    img: "agent1.jpg",
    kicker: "Watcher #2 — Internal Sensors",
    headline: "Concrete strength and building electrics.",
    body: "Two things in one: an ultrasound-style test on how strong the concrete really is inside, and the building's electrical/AC readings (temperature, humidity, power draw). It flags anything that doesn't match what's normal for that exact situation.",
  },
  {
    img: "agent2.jpg",
    kicker: "Watcher #3 — Battery & Fire Risk",
    headline: "Like a battery-health gauge on your phone.",
    body: "It tracks how worn out each battery cell is, how hot it runs, and estimates how many charges are left before it needs replacing — using real data from batteries that were actually run to failure in a lab.",
  },
  {
    img: "agent3.jpg",
    kicker: "Watcher #4 — HVAC / Chiller",
    headline: "Not just “something's wrong” — which specific problem.",
    body: "This one compares live air-conditioning sensor readings to what healthy looks like, then names the specific fault it thinks is happening and how severe it is — like a doctor naming an illness, not just noting a fever.",
  },
  {
    img: "queue.jpg",
    kicker: "The brain's to-do list",
    headline: "Not just “who's sickest” — what's most consequence.",
    body: "The list is ranked by danger AND by what a failure would actually cost. A battery at medium worry can outrank a crack at higher worry, because a battery fire is worse than a slow-growing crack. That weighing is the core of what the “brain” does.",
  },
  {
    img: "feed.jpg",
    kicker: "What happens when something's wrong",
    headline: "It doesn't just alert — it logs a response.",
    body: "When a reading crosses a danger line, the system automatically logs an action, like “throttled battery charging and paged facilities.” In this prototype that's a log entry, not a real switch being flipped — connecting to real building controls is the next step.",
  },
  {
    img: "disaster_before.jpg",
    kicker: "One switch for emergencies (before)",
    headline: "Normally, it weighs risk, cost, and time together.",
    body: "This is the to-do list under everyday conditions — balancing how dangerous something is against how much a failure would cost.",
  },
  {
    img: "disaster_after.jpg",
    kicker: "One switch for emergencies (after)",
    headline: "Flip Disaster Mode, and it stops weighing — it just triages.",
    body: "Same data, same building. One toggle re-sorts the entire list by pure severity, instantly — because in a real emergency you don't have time for nuance, you just need to know what's worst right now.",
  },
  {
    img: null,
    kicker: "The bigger picture",
    headline: "Today: 4 watchers, in one prototype. Designed for many more.",
    body: "Every watcher speaks the same simple language to the brain, so adding a new one — plumbing, elevators, fire panels, air quality, wiring, even a laser scanner that builds a 3D model of the building — means writing one more watcher, not rebuilding the system.",
    foot: "See the full pitch and market case at the main site, or run the live dashboard yourself.",
  },
];

const $ = (s) => document.querySelector(s);
let i = 0;

function render() {
  const s = SLIDES[i];
  const img = $("#shot");
  img.classList.remove("loaded");
  if (s.img) {
    img.src = `img/${s.img}`;
    img.alt = s.headline;
    img.onload = () => img.classList.add("loaded");
    img.closest(".imgwrap").style.display = "";
  } else {
    img.removeAttribute("src");
    img.closest(".imgwrap").style.display = "none";
  }
  $("#kicker").textContent = s.kicker;
  $("#headline").textContent = s.headline;
  $("#body").textContent = s.body;
  $("#foot").textContent = s.foot || "";
  $("#prev").disabled = i === 0;
  $("#next").textContent = i === SLIDES.length - 1 ? "Start over" : "Next →";
  $("#dots").innerHTML = SLIDES.map((_, k) => `<button class="${k === i ? "on" : ""}" data-i="${k}" aria-label="Slide ${k + 1}"></button>`).join("");
  history.replaceState(null, "", `#${i + 1}`);
}

function go(delta) {
  i = (i + delta + SLIDES.length) % SLIDES.length;
  render();
}

$("#prev").addEventListener("click", () => go(-1));
$("#next").addEventListener("click", () => (i === SLIDES.length - 1 ? ((i = 0), render()) : go(1)));
$("#dots").addEventListener("click", (e) => {
  const b = e.target.closest("button[data-i]");
  if (b) { i = Number(b.dataset.i); render(); }
});
document.addEventListener("keydown", (e) => {
  if (e.key === "ArrowRight") go(1);
  if (e.key === "ArrowLeft") go(-1);
});

const fromHash = Number(location.hash.replace("#", ""));
if (fromHash >= 1 && fromHash <= SLIDES.length) i = fromHash - 1;
render();

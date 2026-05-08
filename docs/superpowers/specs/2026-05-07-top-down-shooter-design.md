# Top-Down Shooter — Design Spec

**Date:** 2026-05-07
**File:** `shooter/index.html` (single-file, no build step)

---

## Overview

A top-down twin-stick shooter in the style of Enter the Gungeon. Cartoon/bubbly visual style. The player survives wave after wave of enemies, earns money on kills, and spends it in a between-wave shop on new weapons and upgrades.

---

## Architecture

Single `shooter/index.html` file containing all HTML, CSS, and JavaScript. No dependencies, no build step — open directly in a browser. Canvas-based rendering using `requestAnimationFrame` game loop, identical pattern to `tower-defense/`.

**Internal JS class structure (all in one file, in this order):**
```
Constants → InputHandler → ParticleSystem → Projectile →
Player → Enemy → Shop → Renderer → Game
```

---

## Canvas & Layout

- Canvas: 800×600px
- Top HUD bar: 40px — health, money, wave number, active weapon slots
- Game arena: 800×560px — the playable area
- Shop overlay: rendered over arena between waves

---

## Player

- Represented as a blue circle with an orange gun barrel
- **Movement:** WASD — constant speed, clamped to arena bounds
- **Aiming:** gun barrel always rotates toward mouse cursor position
- **Shooting:** left mouse button fires active weapon; bullets travel in aim direction
- **Health:** starts at 100; takes damage on enemy contact or enemy projectile hit
- **Weapon slots:** holds up to 4 weapons; press 1/2/3/4 to switch; starts with Pistol

---

## Enemies

Three types, all use simple vector steering directly toward the player:

| Type | Shape | Speed | HP | Reward | Behavior |
|------|-------|-------|----|--------|----------|
| Runner | Small red circle | Fast | Low | $5 | Charges player |
| Tank | Large brown rounded square | Slow | High | $15 | Slow charge, high contact damage |
| Shooter | Medium purple circle | Medium | Medium | $10 | Stops at range, fires projectiles at player |

Each enemy has a small health bar above it. Later waves add more enemies and increase counts of Tanks and Shooters.

---

## Weapons

| Weapon | Description | Cost |
|--------|-------------|------|
| Pistol | Single bullet, fast fire rate | Starting weapon |
| Shotgun | 5-bullet spread, slower fire rate | $100 |
| SMG | Rapid fire, weak bullets | $80 |
| Rocket Launcher | Slow large projectile, area splash on impact | $150 |

---

## Upgrades (per weapon, purchasable in shop)

| Upgrade | Effect | Cost |
|---------|--------|------|
| Damage+ | +25% bullet damage | $60 |
| Fire Rate+ | +20% fire rate | $75 |
| Bullet Speed+ | +30% bullet travel speed | $50 |
| Bullet Size+ | Larger hitbox | $40 |

Each upgrade can be purchased up to 3 times per weapon.

---

## Wave Structure

- Wave N spawns a scripted set of enemies (N runners + N/2 tanks + N/3 shooters, rounded)
- Enemies spawn from random positions along arena edges, staggered over ~3 seconds
- Wave ends when all enemies are dead
- Shop opens immediately; player chooses upgrades/weapons
- "Next Wave" button advances to wave N+1
- Player health does **not** reset between waves
- No wave limit — game ends when player HP reaches 0

---

## Shop

Rendered as an overlay panel after each wave. Two sections:
1. **New Weapons** — shows weapons not yet owned; greyed out if unaffordable
2. **Upgrades** — shows upgrade options for currently held weapons; shows current level (e.g. Damage+ ★★☆)

Player can buy multiple items before starting next wave.

---

## Animations & Bubbles

- **Enemy death:** 8 colorful bubbles burst outward from death position, each fades/shrinks over ~0.5s
- **Money drop:** floating `+$N` text rises and fades over ~1s above kill position
- **Hit flash:** enemy sprite flashes white for 1 frame on taking damage
- **Screen shake:** 200ms camera shake when player takes damage
- **Bullet impact:** small spark particle burst (4 particles) on bullet hitting enemy or wall
- **Muzzle flash:** brief circle flash at gun barrel tip on shoot
- **Shop entry:** overlay slides down from top of screen
- **Bubble style:** semi-transparent circles with a lighter inner highlight, matching cartoon palette

---

## Verification

1. Open `shooter/index.html` directly in a browser — no server needed
2. Move player with WASD, aim with mouse, shoot with left click
3. Enemies spawn from edges and path toward player
4. Killing an enemy spawns bubble particles + floating money text
5. Clearing all enemies opens the shop overlay
6. Purchasing a weapon adds it to the HUD; pressing its number key equips it
7. Purchasing an upgrade increases the relevant stat and shows the star level
8. Clicking "Next Wave" closes shop and starts the next wave
9. Player dying shows game over screen with final wave and score

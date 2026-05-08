# Bubble Shooter

A cartoon-style top-down twin-stick shooter built with vanilla JS and HTML5 Canvas. No build step — just open `index.html` in a browser.

## How to Play

- **WASD** — move your character
- **Mouse** — aim your gun
- **Left click** — shoot
- **1 / 2 / 3 / 4** — switch between owned weapons

## Game Loop

Survive waves of enemies. Kill them to earn money. Spend money in the shop between waves on new weapons and upgrades. The game ends when your HP hits zero.

## Enemies

| Enemy | Look | Behavior |
|-------|------|----------|
| Runner | Small red circle | Fast, low HP — charges straight at you |
| Tank | Large brown square | Slow, very high HP — deals heavy contact damage |
| Shooter | Medium purple circle | Keeps its distance and fires projectiles at you |

Wave N spawns N Runners + N/2 Tanks + N/3 Shooters (rounded down), staggered from random arena edges.

## Weapons

| Weapon | Cost | Description |
|--------|------|-------------|
| Pistol | Free | Single fast bullet — starting weapon |
| Shotgun | $100 | 5-bullet spread — great for crowds |
| SMG | $80 | Rapid fire, lower damage per bullet |
| Rocket Launcher | $150 | Slow projectile with area splash on impact |

## Upgrades

Each weapon can be upgraded up to 3 times per stat in the between-wave shop:

- **Damage+** — +25% bullet damage ($60)
- **Fire Rate+** — +20% faster fire rate ($75)
- **Bullet Speed+** — +30% bullet travel speed ($50)
- **Bullet Size+** — larger bullet hitbox ($40)

## Animations

- Enemy deaths trigger a burst of 8 colorful bubbles
- Floating `+$N` text rises from each kill
- Bullet impacts produce spark particles
- Taking a hit from an enemy projectile shakes the screen
- Gun barrel flashes on fire

## Technical

Single file: all HTML, CSS, and JavaScript lives in `index.html`. Class order: `Constants → InputHandler → ParticleSystem → Projectile → Player → Enemy → Shop → Renderer → Game`.
